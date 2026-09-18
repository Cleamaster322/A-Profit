from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Brand, CarData, Configuration, Generation, Model, Protocol, ProtocolPhoto


class ProtocolWorkflowTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.measurer = self.create_user("measurer", "measurer")
		self.other_measurer = self.create_user("other-measurer", "measurer")
		self.operator = self.create_user("operator", "operator")
		self.manager = self.create_user("manager", "manager")
		self.brand = Brand.objects.create(
			name="Test KIA",
			link="https://example.com/test-kia",
		)
		self.model = Model.objects.create(
			name="Test RIO",
			link="https://example.com/test-rio",
			brand=self.brand,
		)
		self.generation = Generation.objects.create(
			name="Test generation",
			link="https://example.com/test-generation",
			model=self.model,
			date_start="01.2020",
			date_end="12.2021",
		)
		self.other_generation = Generation.objects.create(
			name="Other generation",
			link="https://example.com/other-generation",
			model=self.model,
			date_start="01.2022",
			date_end="12.2023",
		)
		self.configuration = Configuration.objects.create(
			name="Test configuration",
			link="https://example.com/test-configuration",
			generation=self.generation,
			date_start="01.2020",
			date_end="12.2021",
		)
		self.other_configuration = Configuration.objects.create(
			name="Other configuration",
			link="https://example.com/other-configuration",
			generation=self.other_generation,
			date_start="01.2022",
			date_end="12.2023",
		)
		CarData.objects.create(
			configuration=self.configuration,
			manufacture_year=2020,
			front_tires="185/65R15",
			rear_tires="185/65R15",
			fuel_type="petrol",
			transmission="automatic",
			drive_type="front",
		)
		CarData.objects.create(
			configuration=self.other_configuration,
			manufacture_year=2022,
			front_tires="195/55R16",
			rear_tires="195/55R16",
			fuel_type="petrol",
			transmission="automatic",
			drive_type="front",
		)
		self.protocol = Protocol.objects.create(
			user=self.measurer,
			model=self.model,
			protocol_date=date(2020, 5, 1),
			protocol_number="00001",
			owner_name="Тестовый владелец",
			brand_name="KIA",
			commercial_name="RIO",
			status="measurement",
		)

	@staticmethod
	def create_user(username, role):
		user = User.objects.create_user(username=username, password="test-password")
		user.groups.add(Group.objects.get_or_create(name=role)[0])
		return user

	def authenticate(self, user):
		self.client.force_authenticate(user=user)

	def post(self, path, data=None):
		return self.client.post(path, data or {}, format="json")

	def test_full_protocol_workflow_reaches_approved(self):
		self.authenticate(self.measurer)

		start_response = self.post(
			f"/cars/protocols/{self.protocol.id}/start-editing/"
		)
		self.assertEqual(start_response.status_code, 200)

		submit_response = self.post(
			f"/cars/protocols/{self.protocol.id}/submit-to-operator/"
		)
		self.assertEqual(submit_response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "operator")
		self.assertIsNone(self.protocol.locked_by_id)

		self.authenticate(self.operator)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)
		review_response = self.post(
			f"/cars/protocols/{self.protocol.id}/submit-for-review/"
		)
		self.assertEqual(review_response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "review")
		self.assertIsNone(self.protocol.locked_by_id)

		self.authenticate(self.manager)
		approve_response = self.post(
			f"/cars/protocols/{self.protocol.id}/approve/"
		)
		self.assertEqual(approve_response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "approved")
		self.assertIsNone(self.protocol.locked_by_id)

	def test_reviewer_can_return_protocol_for_revision(self):
		self.protocol.status = "review"
		self.protocol.save(update_fields=["status"])
		self.authenticate(self.manager)

		response = self.post(
			f"/cars/protocols/{self.protocol.id}/cancel/",
			{"revision_comment": "Нужно уточнить результаты замера"},
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "revision")
		self.assertTrue(self.protocol.returned_for_revision)
		self.assertEqual(
			self.protocol.revision_comment,
			"Нужно уточнить результаты замера",
		)
		self.assertEqual(self.protocol.cancelled_by_id, self.manager.id)
		self.assertIsNone(self.protocol.locked_by_id)

	def test_measurer_cannot_access_another_measurers_protocol(self):
		self.authenticate(self.other_measurer)

		response = self.client.get(f"/cars/protocols/{self.protocol.id}/")

		self.assertEqual(response.status_code, 403)

	def test_locked_protocol_cannot_be_opened_by_second_user(self):
		self.authenticate(self.measurer)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)

		self.authenticate(self.operator)
		response = self.post(
			f"/cars/protocols/{self.protocol.id}/start-editing/"
		)

		self.assertEqual(response.status_code, 423)
		self.assertEqual(response.data["locked_by_id"], self.measurer.id)

	def test_operator_cannot_approve_protocol(self):
		self.protocol.status = "review"
		self.protocol.save(update_fields=["status"])
		self.authenticate(self.operator)

		response = self.post(f"/cars/protocols/{self.protocol.id}/approve/")

		self.assertEqual(response.status_code, 403)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "review")

	def test_revision_protocol_can_be_sent_back_to_review(self):
		self.protocol.status = "revision"
		self.protocol.returned_for_revision = True
		self.protocol.revision_comment = "Исправить данные"
		self.protocol.save(
			update_fields=["status", "returned_for_revision", "revision_comment"]
		)

		self.authenticate(self.operator)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)
		response = self.post(
			f"/cars/protocols/{self.protocol.id}/submit-for-review/"
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "review")
		self.assertFalse(self.protocol.returned_for_revision)
		self.assertIsNone(self.protocol.revision_comment)

	def test_only_lock_owner_can_send_heartbeat(self):
		self.authenticate(self.measurer)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)

		self.authenticate(self.operator)
		response = self.post(f"/cars/protocols/{self.protocol.id}/heartbeat/")

		self.assertEqual(response.status_code, 403)

	def test_reviewer_can_release_another_users_lock(self):
		self.authenticate(self.measurer)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)

		self.authenticate(self.manager)
		response = self.post(
			f"/cars/protocols/{self.protocol.id}/manager-release-lock/"
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertIsNone(self.protocol.locked_by_id)
		self.assertIsNone(self.protocol.locked_at)

	def test_operator_list_excludes_measurement_and_review_protocols(self):
		Protocol.objects.create(
			user=self.measurer,
			protocol_number="00002",
			status="operator",
		)
		Protocol.objects.create(
			user=self.measurer,
			protocol_number="00003",
			status="review",
		)

		self.authenticate(self.operator)
		response = self.client.get("/cars/protocols/")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			{item["status"] for item in response.data["results"]},
			{"operator"},
		)

	def test_approved_protocol_cannot_be_started_for_editing(self):
		self.protocol.status = "approved"
		self.protocol.save(update_fields=["status"])
		self.authenticate(self.measurer)

		response = self.post(
			f"/cars/protocols/{self.protocol.id}/start-editing/"
		)

		self.assertEqual(response.status_code, 403)

	def test_configuration_must_belong_to_selected_generation(self):
		self.protocol.locked_by = self.measurer
		self.protocol.locked_at = timezone.now()
		self.protocol.save(update_fields=["locked_by", "locked_at"])
		self.authenticate(self.measurer)

		response = self.post(
			f"/cars/protocols/{self.protocol.id}/select-configuration/",
			{
				"generation_id": self.generation.id,
				"configuration_id": self.other_configuration.id,
				"manufacture_date": "2020-05",
			},
		)

		self.assertEqual(response.status_code, 400)
		self.protocol.refresh_from_db()
		self.assertIsNone(self.protocol.configuration_id)

	def test_configuration_must_match_manufacture_month(self):
		self.protocol.locked_by = self.measurer
		self.protocol.locked_at = timezone.now()
		self.protocol.save(update_fields=["locked_by", "locked_at"])
		self.authenticate(self.measurer)

		response = self.post(
			f"/cars/protocols/{self.protocol.id}/select-configuration/",
			{
				"generation_id": self.generation.id,
				"configuration_id": self.configuration.id,
				"manufacture_date": "2022-05",
			},
		)

		self.assertEqual(response.status_code, 400)
		self.protocol.refresh_from_db()
		self.assertIsNone(self.protocol.configuration_id)

	def test_valid_generation_configuration_and_month_are_saved(self):
		self.protocol.locked_by = self.measurer
		self.protocol.locked_at = timezone.now()
		self.protocol.save(update_fields=["locked_by", "locked_at"])
		self.authenticate(self.measurer)

		response = self.post(
			f"/cars/protocols/{self.protocol.id}/select-configuration/",
			{
				"generation_id": self.generation.id,
				"configuration_id": self.configuration.id,
				"manufacture_date": "2020-05",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.generation_id, self.generation.id)
		self.assertEqual(self.protocol.configuration_id, self.configuration.id)
		self.assertEqual(self.protocol.manufacture_date, date(2020, 5, 1))

	def test_measurer_cannot_access_foreign_protocol_resources(self):
		photo = ProtocolPhoto.objects.create(
			protocol=self.protocol,
			photo_type="other",
			file_path="e2e/foreign-photo.jpg",
		)
		self.authenticate(self.other_measurer)

		protected_get_urls = [
			f"/cars/protocols/{self.protocol.id}/",
			f"/cars/protocols/{self.protocol.id}/full/",
			f"/cars/protocols/{self.protocol.id}/measurement/",
			f"/cars/protocols/{self.protocol.id}/photos/",
			f"/cars/protocols/{self.protocol.id}/generate-docx/",
			f"/cars/protocols/{self.protocol.id}/preview-pdf/",
		]

		for url in protected_get_urls:
			with self.subTest(url=url):
				response = self.client.get(url)
				self.assertEqual(response.status_code, 403)
				self.assertEqual(response.data["code"], "permission_denied")
				self.assertIn("detail", response.data)

		self.assertEqual(
			self.client.patch(
				f"/cars/protocols/{self.protocol.id}/update/",
				{"owner_name": "Подмена"},
				format="json",
			).status_code,
			403,
		)
		self.assertEqual(
			self.client.patch(
				f"/cars/protocol-photos/{photo.id}/update/",
				{"sort_order": 99},
				format="json",
			).status_code,
			403,
		)
		self.assertEqual(
			self.client.delete(f"/cars/protocol-photos/{photo.id}/delete/").status_code,
			403,
		)

	def test_protocol_serializer_rejects_manual_service_field_changes(self):
		self.authenticate(self.measurer)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)

		response = self.client.patch(
			f"/cars/protocols/{self.protocol.id}/update/",
			{
				"protocol_number": "HACKED-NUMBER",
				"status": "approved",
				"user": self.other_measurer.id,
				"locked_by": self.other_measurer.id,
				"locked_at": "2030-01-01T00:00:00Z",
				"cancelled_by": self.other_measurer.id,
				"owner_name": "Разрешенное изменение",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.protocol_number, "00001")
		self.assertEqual(self.protocol.status, "measurement")
		self.assertEqual(self.protocol.user_id, self.measurer.id)
		self.assertEqual(self.protocol.locked_by_id, self.measurer.id)
		self.assertEqual(self.protocol.owner_name, "Разрешенное изменение")
