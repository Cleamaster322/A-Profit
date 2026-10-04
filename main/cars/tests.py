from datetime import date
from decimal import Decimal
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from docx import Document
from rest_framework.test import APIClient

from .models import (
	Brand,
	CarData,
	Configuration,
	Generation,
	Model,
	Protocol,
	ProtocolBrake,
	ProtocolMeasurement,
	ProtocolPhoto,
)
from .serializers import (
	ConfigurationSerializer,
	ProtocolBrakeSerializer,
	ProtocolLightSerializer,
	ProtocolMeasurementSerializer,
	ProtocolPowerSupplySerializer,
	ProtocolTestConditionSerializer,
)
from .services.protocol_docx.calculations import (
	calc_light_absorption_uncertainty,
	standard_headlight_uncertainty_cd,
	u_control_force_n,
	u_glass_transparency_pct,
	u_noise_db,
	u_scale_kg,
	u_speed_kmh,
	u_steering_backlash_deg,
	u_turn_signal_frequency_hz,
	u_vehicle_height_mm,
)
from .services.test_docx import generate_protocol_docx
from .services.protocol_docx.applicability import build_applicability_values
from .services.protocol_docx.context import (
	build_light_device_row_values,
	build_dynamic_result_values,
	build_eco_values,
	build_front_fog_values,
	build_rear_fog_values,
	build_tire_depth_values,
)
from .services.protocol_docx.renderer import process_document_conditions
from .services.protocol_docx.v6_placeholder_migration import (
	add_v6_context_aliases,
	create_v6_template,
	load_v5_v6_mappings,
)


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
			vehicle_length_mm=3800,
			vehicle_width_mm=1680,
			vehicle_height_mm=1510,
			vehicle_weight_kg=990,
			engine_model="Test engine",
			engine_power_kw=45,
			cylinder_layout="inline",
			cylinders_count=3,
			turbo_present=False,
			front_brakes="дисковые",
			rear_brakes="дисковые",
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

	def test_superuser_can_lock_and_update_protocol(self):
		admin = User.objects.create_superuser(
			username="admin",
			email="admin@example.com",
			password="test-password",
		)
		self.authenticate(admin)

		lock_response = self.post(
			f"/cars/protocols/{self.protocol.id}/start-editing/"
		)
		self.assertEqual(lock_response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.locked_by_id, admin.id)

		update_response = self.client.patch(
			f"/cars/protocols/{self.protocol.id}/update/",
			{"owner_name": "Updated by admin"},
			format="json",
		)
		self.assertEqual(update_response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.owner_name, "Updated by admin")

	def test_superuser_can_update_approved_protocol_despite_foreign_lock(self):
		self.protocol.status = "approved"
		self.protocol.locked_by = self.other_measurer
		self.protocol.locked_at = timezone.now()
		self.protocol.save(update_fields=["status", "locked_by", "locked_at"])
		admin = User.objects.create_superuser(
			username="admin-all-rights",
			email="admin-all-rights@example.com",
			password="test-password",
		)
		self.authenticate(admin)

		response = self.client.patch(
			f"/cars/protocols/{self.protocol.id}/update/",
			{"owner_name": "Updated by full-access admin"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.owner_name, "Updated by full-access admin")

	def test_measurement_api_saves_pneumatic_suspension_presence(self):
		ProtocolMeasurement.objects.create(protocol=self.protocol)
		self.authenticate(self.measurer)
		self.assertEqual(
			self.post(f"/cars/protocols/{self.protocol.id}/start-editing/").status_code,
			200,
		)

		response = self.client.patch(
			f"/cars/protocols/{self.protocol.id}/measurement/update/",
			{"pneumatic_suspension_present": True},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		measurement = ProtocolMeasurement.objects.get(protocol=self.protocol)
		self.assertTrue(measurement.pneumatic_suspension_present)

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

	def test_superuser_returns_approved_protocol_to_operator_and_can_edit(self):
		self.protocol.status = "approved"
		self.protocol.returned_for_revision = True
		self.protocol.revision_comment = "Previously returned"
		self.protocol.cancelled_by = self.manager
		self.protocol.cancelled_at = timezone.now()
		self.protocol.save(
			update_fields=[
				"status",
				"returned_for_revision",
				"revision_comment",
				"cancelled_by",
				"cancelled_at",
			]
		)
		admin = User.objects.create_superuser(
			username="admin-return",
			email="admin-return@example.com",
			password="test-password",
		)
		self.authenticate(admin)

		response = self.post(f"/cars/protocols/{self.protocol.id}/return-to-draft/")

		self.assertEqual(response.status_code, 200)
		self.protocol.refresh_from_db()
		self.assertEqual(self.protocol.status, "operator")
		self.assertEqual(self.protocol.locked_by_id, admin.id)
		self.assertIsNotNone(self.protocol.locked_at)
		self.assertFalse(self.protocol.returned_for_revision)
		self.assertIsNone(self.protocol.revision_comment)
		self.assertIsNone(self.protocol.cancelled_by_id)
		self.assertIsNone(self.protocol.cancelled_at)

		update_response = self.client.patch(
			f"/cars/protocols/{self.protocol.id}/update/",
			{"owner_name": "Reopened by admin"},
			format="json",
		)
		self.assertEqual(update_response.status_code, 200)

	def test_operator_cannot_return_approved_protocol_to_operator(self):
		self.protocol.status = "approved"
		self.protocol.save(update_fields=["status"])
		self.authenticate(self.operator)

		response = self.post(f"/cars/protocols/{self.protocol.id}/return-to-draft/")

		self.assertEqual(response.status_code, 403)

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
		measurement = ProtocolMeasurement.objects.get(protocol=self.protocol)
		self.assertEqual(measurement.vehicle_length_mm, Decimal("3800"))
		self.assertEqual(measurement.vehicle_width_mm, Decimal("1680"))
		self.assertEqual(measurement.vehicle_height_mm, Decimal("1510"))
		self.assertEqual(measurement.vehicle_weight_kg, Decimal("990"))
		self.assertEqual(measurement.wheel_formula, "4x2_front")
		self.assertEqual(measurement.engine_model, "Test engine")
		self.assertEqual(measurement.fuel_type, "petrol")
		self.assertEqual(
			ProtocolBrake.objects.get(protocol=self.protocol).service_brake_type,
			"disc_disc",
		)
		measurement = ProtocolMeasurement.objects.get(protocol=self.protocol)
		self.assertEqual(measurement.vehicle_length_mm, Decimal("3800"))
		self.assertEqual(measurement.vehicle_width_mm, Decimal("1680"))
		self.assertEqual(measurement.vehicle_height_mm, Decimal("1510"))
		self.assertEqual(measurement.vehicle_weight_kg, Decimal("990"))
		self.assertEqual(measurement.wheel_formula, "4x2_front")
		self.assertEqual(measurement.engine_model, "Test engine")
		self.assertEqual(measurement.fuel_type, "petrol")

	def test_configuration_import_preserves_measured_and_dash_values(self):
		measurement = ProtocolMeasurement.objects.create(
			protocol=self.protocol,
			vehicle_length_mm=Decimal("4001"),
			vehicle_width_mm=None,
			dash_fields=["vehicle_width_mm"],
		)
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
		measurement.refresh_from_db()
		self.assertEqual(measurement.vehicle_length_mm, Decimal("4001"))
		self.assertIsNone(measurement.vehicle_width_mm)
		self.assertEqual(measurement.vehicle_height_mm, Decimal("1510"))

	def test_configuration_import_normalizes_full_drive_to_four_by_four(self):
		CarData.objects.filter(configuration=self.configuration).update(drive_type="full")
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
		measurement = ProtocolMeasurement.objects.get(protocol=self.protocol)
		self.assertEqual(measurement.wheel_formula, "4x4")

	def test_configuration_payload_exposes_car_data_dimensions(self):
		payload = ConfigurationSerializer(self.configuration).data

		self.assertEqual(payload["vehicle_length_mm"], 3800)
		self.assertEqual(payload["vehicle_width_mm"], 1680)
		self.assertEqual(payload["vehicle_height_mm"], 1510)
		self.assertEqual(payload["vehicle_weight_kg"], 990)
		self.assertEqual(payload["engine_model"], "Test engine")
		self.assertEqual(payload["engine_power_kw"], 45)

	def test_configuration_import_preserves_measured_and_dash_values(self):
		measurement = ProtocolMeasurement.objects.create(
			protocol=self.protocol,
			vehicle_length_mm=Decimal("4001"),
			vehicle_width_mm=None,
			dash_fields=["vehicle_width_mm"],
		)
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
		measurement.refresh_from_db()
		self.assertEqual(measurement.vehicle_length_mm, Decimal("4001"))
		self.assertIsNone(measurement.vehicle_width_mm)
		self.assertEqual(measurement.vehicle_height_mm, Decimal("1510"))

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


class ProtocolTemplateGenerationTests(SimpleTestCase):
	def test_generator_selects_old_v5_and_v6_templates(self):
		protocol = SimpleNamespace(id=42)

		with TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				with patch(
					"cars.services.test_docx.build_protocol_docx_context",
					return_value={"example": "value"},
				), patch(
					"cars.services.test_docx.render_protocol_docx",
					side_effect=lambda template_path, output_path, context: output_path,
				) as render:
					old_output = generate_protocol_docx(protocol)
					v5_output = generate_protocol_docx(protocol, "v5")
					with patch(
						"cars.services.test_docx.add_v6_context_aliases"
					) as add_aliases:
						v6_output = generate_protocol_docx(protocol, "v6")
						add_aliases.assert_called_once_with({"example": "value"})

		self.assertEqual(old_output.name, "protocol_42_old.docx")
		self.assertEqual(v5_output.name, "protocol_42_v5.docx")
		self.assertEqual(v6_output.name, "protocol_42_v6.docx")
		self.assertEqual(
			[
				call.kwargs["template_path"].name
				for call in render.call_args_list
			],
			[
				"protocol_template.docx",
				"protocol_template_v5_source.docx",
				"protocol_template_v6_source.docx",
			],
		)

	def test_v6_aliases_and_template_cover_the_rename_map(self):
		placeholder_renames, condition_renames = load_v5_v6_mappings()
		self.assertEqual(len(placeholder_renames), 253)

		context = {name: name for name in placeholder_renames}
		for old_tag in condition_renames:
			match = re.fullmatch(
				r"{%\s*tr\s+if\s+(?:not\s+)?([A-Za-z0-9_]+)\s*%}",
				old_tag,
			)
			if match:
				context.setdefault(match.group(1), False)
		context["rear_fog_a_8_13_2_conclusion"] = "-"

		add_v6_context_aliases(context)
		self.assertEqual(context["a_8_13_2_conclusion"], "-")
		for new_name in placeholder_renames.values():
			self.assertIn(new_name, context)

		with TemporaryDirectory() as temp_dir:
			template_path = create_v6_template(
				Path(temp_dir) / "protocol_template_v6_source.docx"
			)
			self.assertGreater(template_path.stat().st_size, 0)
			Document(template_path)

	def test_excel_reason_placeholders_are_available_for_docx(self):
		protocol = SimpleNamespace(registration_number=None)
		measurement = SimpleNamespace()
		values = build_applicability_values(protocol, measurement, SimpleNamespace(), {})

		self.assertEqual(
			values["applicable_1_2_1"],
			"не применяется (на ТС отсутствует государственный регистрационный знак)",
		)
		self.assertEqual(
			values["applicable_8_13_1"],
			"не указано",
		)
		self.assertIn("applicable_3_1", values)
		self.assertFalse(any(key.startswith("not_applicable_") for key in values))


class ProtocolApplicabilityTests(SimpleTestCase):
	def test_tire_depth_1072_is_always_output_and_1073_is_winter_only(self):
		measurement = SimpleNamespace(
			tire_depth_fl_mm=Decimal("5.6"),
			tire_depth_fr_mm=Decimal("5.4"),
			tire_depth_rl_mm=Decimal("5.2"),
			tire_depth_rr_mm=Decimal("5.0"),
		)
		cases = (
			("summer", True, False),
			("winter", False, True),
		)

		for season, summer_present, winter_present in cases:
			with self.subTest(season=season):
				values = build_tire_depth_values(
					SimpleNamespace(tire_season=season),
					measurement,
				)

				self.assertEqual(values["summer_tires_present"], summer_present)
				self.assertEqual(values["winter_tires_present"], winter_present)
				self.assertEqual(values["tire_depth_fl_10_7_2"], "5,6 мм")
				self.assertIn("5,6 мм ± 0,05 мм", values["full_result_a_10_7_2"])

				if season == "summer":
					self.assertEqual(
						values["full_result_a_10_7_3"],
						"не применяется (на ТС установлены летние шины)",
					)
				else:
					self.assertEqual(values["tire_depth_fl_10_7_3"], "5,6 мм")
					self.assertIn("5,6 мм ± 0,05 мм", values["full_result_a_10_7_3"])

	def test_front_fog_clause_8_10_1_splits_status_and_conclusion(self):
		absent = build_front_fog_values(SimpleNamespace(front_fog_count=0))
		self.assertEqual(
			absent["front_fog_a_8_10_1_status"],
			"не применяется (в ТС отсутствуют передние противотуманные фары)",
		)
		self.assertEqual(absent["front_fog_a_8_10_1_conclusion"], "-")
		for field in (
			"fog_light_left_distance_8_10_1",
			"fog_light_right_distance_8_10_1",
			"u_fog_light_left_distance_8_10_1",
			"u_fog_light_right_distance_8_10_1",
			"fog_light_lower_point_8_10_2",
			"fog_light_upper_point_8_10_2",
			"u_fog_light_lower_point_8_10_2",
			"u_fog_light_upper_point_8_10_2",
		):
			self.assertEqual(absent[field], "")
		for clause in ("8_10_2", "8_10_3"):
			self.assertEqual(
				absent[f"front_fog_a_{clause}_status"],
				"не применяется (в ТС отсутствуют передние противотуманные фары)",
			)
			self.assertEqual(absent[f"front_fog_a_{clause}_conclusion"], "-")

		present = build_front_fog_values(SimpleNamespace(
			front_fog_count=2,
			fog_light_left_distance_mm=200,
			fog_light_right_distance_mm=210,
		))
		self.assertEqual(present["front_fog_a_8_10_1_status"], "соответствует")
		self.assertIn("Результат:", present["front_fog_a_8_10_1_conclusion"])
		self.assertIn("±", present["front_fog_a_8_10_1_conclusion"])
		self.assertIn("Левая", present["front_fog_a_8_10_1_conclusion"])
		self.assertIn("Правая", present["front_fog_a_8_10_1_conclusion"])
		self.assertEqual(present["front_fog_a_8_10_2_status"], "соответствует")
		self.assertIn("Результат:", present["front_fog_a_8_10_2_conclusion"])
		self.assertIn("±", present["front_fog_a_8_10_2_conclusion"])
		self.assertEqual(present["front_fog_a_8_10_3_status"], "соответствует")
		self.assertNotEqual(present["front_fog_a_8_10_3_conclusion"], "-")

	def test_rear_fog_condition_placeholders_cover_all_count_states(self):
		cases = (
			(None, False, False, True),
			(0, False, False, True),
			(1, True, False, False),
			(2, False, True, False),
		)

		for count, one_lamp, two_lamps, absent in cases:
			with self.subTest(rear_fog_count=count):
				values = build_light_device_row_values(
					SimpleNamespace(rear_fog_count=count)
				)

				self.assertEqual(values["rear_fog_one_lamp_present"], one_lamp)
				self.assertEqual(values["rear_fog_two_lamps_present"], two_lamps)
				self.assertEqual(values["rear_fog_absent"], absent)

	def test_rear_fog_width_requirement_applies_only_to_one_lamp(self):
		protocol = SimpleNamespace()
		measurement = SimpleNamespace()
		cases = (
			(None, "не применяется (в ТС отсутствуют задние противотуманные фонари)"),
			(0, "не применяется (в ТС отсутствуют задние противотуманные фонари)"),
			(1, "соответствует"),
			(2, "не применяется (в ТС имеется два задних противотуманных фонаря)"),
		)

		for count, expected in cases:
			with self.subTest(rear_fog_count=count):
				light = SimpleNamespace(rear_fog_count=count)
				values = build_dynamic_result_values(protocol, measurement, light)

				self.assertEqual(values["result_a_8_13_1_status"], expected)
				self.assertEqual(values["rear_fog_a_8_13_1_status"], expected)
				self.assertEqual(
					values["rear_fog_a_8_13_1_conclusion"],
					values["result_a_8_13_1_conclusion"],
				)

	def test_rear_fog_clause_8_13_2_splits_status_and_conclusion(self):
		absent = build_rear_fog_values(SimpleNamespace(rear_fog_count=0))
		self.assertEqual(
			absent["rear_fog_a_8_13_2_status"],
			"не применяется (в ТС отсутствуют задние противотуманные фонари)",
		)
		self.assertEqual(absent["rear_fog_a_8_13_2_conclusion"], "-")

		present = build_rear_fog_values(SimpleNamespace(
			rear_fog_count=1,
			rear_fog_upper_point_mm=500,
			rear_fog_lower_point_mm=400,
		))
		self.assertEqual(present["rear_fog_a_8_13_2_status"], "соответствует")
		self.assertIn("Результат:", present["rear_fog_a_8_13_2_conclusion"])
		self.assertIn("±", present["rear_fog_a_8_13_2_conclusion"])

	def test_dynamic_non_applicability_statuses_use_excel_messages(self):
		values = build_dynamic_result_values(
			SimpleNamespace(tire_season="summer", has_spikes=False),
			SimpleNamespace(
				glonass_button_present=False,
				steering_lock_present=False,
				steps_present=False,
				opening_roof_present=False,
				spare_wheel_present=False,
				gas_equipment_present=False,
			),
			SimpleNamespace(
				front_fog_count=0,
				rear_fog_count=0,
				daytime_running_light_count=0,
				parking_light_count=0,
				rear_parking_light_count=0,
				adaptive_front_lighting_count=0,
				headlight_washer_present=False,
			),
		)

		self.assertEqual(
			values["result_a_3_2_status"],
			"не применяется (пункт Постановления Правительства)",
		)
		self.assertEqual(
			values["result_a_8_7_status"],
			"не применяется (в фарах ТС установлены источники света отличные от описанных в п. А.8.7)",
		)
		self.assertEqual(
			values["result_a_8_20_3_status"],
			"не применяется (ТС не оснащено устройствами фароочистки  и автоматическим корректирующим устройством угла наклона фар (не предусмотрено конструкцией))",
		)
		self.assertEqual(
			values["result_a_10_5_status"],
			"не применяется (на ТС установлены летние шины)",
		)

	def test_a87_and_a8203_depend_only_on_adaptive_front_lighting(self):
		protocol = SimpleNamespace()
		measurement = SimpleNamespace()
		cases = (
			(None, False),
			(0, True),
			(2, False),
			(2, True),
		)

		for adaptive_count, washer_present in cases:
			with self.subTest(
				adaptive_count=adaptive_count,
				washer_present=washer_present,
			):
				light = SimpleNamespace(
					adaptive_front_lighting_count=adaptive_count,
					headlight_washer_present=washer_present,
				)
				dynamic_values = build_dynamic_result_values(
					protocol,
					measurement,
					light,
				)
				applicability = build_applicability_values(
					protocol,
					measurement,
					light,
					dynamic_values,
				)

				expected = (
					"соответствует"
					if adaptive_count == 2
					else "не применяется (в фарах ТС установлены источники света "
					"отличные от описанных в п. А.8.7)"
				)
				expected_8_20_3 = (
					"соответствует"
					if adaptive_count == 2
					else "не применяется (ТС не оснащено устройствами фароочистки  и "
					"автоматическим корректирующим устройством угла наклона фар "
					"(не предусмотрено конструкцией))"
				)
				self.assertEqual(dynamic_values["result_a_8_7_status"], expected)
				self.assertEqual(applicability["applicable_8_7"], expected)
				self.assertEqual(
					applicability["applicable_8_20_3"],
					expected_8_20_3,
				)

	def test_applicability_output_uses_one_key_per_clause(self):
		protocol = SimpleNamespace(tire_season="summer", has_spikes=False)
		measurement = SimpleNamespace(
			fuel_type="diesel",
			mileage_km=1000,
			glonass_button_present=False,
		)
		light = SimpleNamespace()
		dynamic_values = build_dynamic_result_values(protocol, measurement, light)
		values = build_applicability_values(protocol, measurement, light, dynamic_values)

		self.assertEqual(
			values["applicable_3_1"],
			"не применяется (пункт Постановления Правительства)",
		)
		self.assertEqual(
			values["applicable_21_7"],
			"не применяется (пробег ТС менее 3000 км)",
		)
		self.assertEqual(
			values["applicable_2_1"],
			"не применяется (ТС не используется для коммерческих перевозок)",
		)
		self.assertEqual(values["applicable_3_3_4"], "не указано")
		self.assertEqual(
			values["applicable_5_1_2_2"],
			"не применяется (ТС оборудован двухконтурной тормозной системой. "
			"Запасная тормозная система входит в состав рабочей тормозной системы "
			"и не оснащается независимым органом управления)",
		)
		self.assertEqual(
			values["applicable_8_19"],
			"не применяется (на ТС отсутствует светоотражающая маркировка)",
		)
		self.assertEqual(
			build_applicability_values(
				SimpleNamespace(vehicle_category="M1"),
				SimpleNamespace(fuel_type="diesel", vehicle_weight_kg=2000),
				SimpleNamespace(),
				{},
			)["applicable_21_3"],
			"не указано",
		)
		self.assertEqual(
			values["applicable_8_20_3"],
			"не применяется (ТС не оснащено устройствами фароочистки  и "
			"автоматическим корректирующим устройством угла наклона фар "
			"(не предусмотрено конструкцией))",
		)

		washer_present_light = SimpleNamespace(
			headlight_washer_present=True,
			adaptive_front_lighting_count=2,
		)
		washer_present_dynamic_values = build_dynamic_result_values(
			protocol,
			measurement,
			washer_present_light,
		)
		washer_present_values = build_applicability_values(
			protocol,
			measurement,
			washer_present_light,
			washer_present_dynamic_values,
		)
		self.assertEqual(washer_present_values["applicable_8_20_3"], "соответствует")
		for clause in ("8_18_1", "8_18_2", "8_18_3", "8_18_4"):
			self.assertEqual(values[f"applicable_{clause}"], "отсутствие")
		self.assertIn("applicable_21_8", values)
		self.assertFalse(any(key.startswith("not_applicable_") for key in values))

	def test_a20_5_1_depends_only_on_electric_engine(self):
		cases = (
			(
				"electric",
				"fixed_cap",
				"не применяется (ТС оборудовано только электродвигателем)",
			),
			(
				"petrol",
				"fixed_cap",
				"не применяется (на ТС отсутствует несъемная крышка наливной горловины топливного бака)",
			),
			(
				"diesel",
				None,
				"не применяется (на ТС отсутствует несъемная крышка наливной горловины топливного бака)",
			),
		)

		for fuel_type, protection_measure, expected in cases:
			with self.subTest(fuel_type=fuel_type, protection_measure=protection_measure):
				values = build_applicability_values(
					SimpleNamespace(),
					SimpleNamespace(
						fuel_type=fuel_type,
						fuel_tank_leak_protection_measure=protection_measure,
					),
					SimpleNamespace(),
					{},
				)

				self.assertEqual(values["applicable_20_5_1"], expected)

	def test_a21_4_to_a21_6_apply_only_to_non_electric_engines(self):
		for fuel_type in ("electric", "petrol", "diesel"):
			with self.subTest(fuel_type=fuel_type):
				values = build_applicability_values(
					SimpleNamespace(),
					SimpleNamespace(fuel_type=fuel_type),
					SimpleNamespace(),
					{},
				)
				expected = (
					"не применяется (ТС оборудовано только электродвигателем)"
					if fuel_type == "electric"
					else "соответствует"
				)

				for clause in ("21_4", "21_5", "21_6"):
					self.assertEqual(values[f"applicable_{clause}"], expected)

	def test_a23_1_exposes_electric_and_numeric_docx_conditions(self):
		for fuel_type, is_electric in (
			("electric", True),
			("petrol", False),
			("diesel", False),
			("hybrid", False),
			(None, False),
		):
			with self.subTest(fuel_type=fuel_type):
				values = build_dynamic_result_values(
					SimpleNamespace(),
					SimpleNamespace(fuel_type=fuel_type),
					SimpleNamespace(),
				)

				self.assertEqual(values["a_23_1_electric"], is_electric)
				self.assertEqual(values["a_23_1_numeric"], not is_electric)

	def test_a23_2_has_separate_applicability_and_conclusion_placeholders(self):
		protocol = SimpleNamespace()
		light = SimpleNamespace()
		cases = (
			(
				"electric",
				"не применяется (ТС оборудовано только электродвигателем)",
				"-",
			),
			(
				"petrol",
				"соответствует",
				"Соответствует требованиям\nТР ТС 018/2011\nПриложения N 8 п.9.10",
			),
		)

		for fuel_type, expected_status, expected_conclusion in cases:
			with self.subTest(fuel_type=fuel_type):
				measurement = SimpleNamespace(fuel_type=fuel_type)
				context = build_dynamic_result_values(protocol, measurement, light)
				applicability = build_applicability_values(
					protocol,
					measurement,
					light,
					context,
				)

				self.assertEqual(context["result_a_23_2_status"], expected_status)
				self.assertEqual(
					context["result_a_23_2_conclusion"],
					expected_conclusion,
				)
				self.assertEqual(applicability["applicable_23_2"], expected_status)

	def test_a24_6_has_separate_applicability_and_conclusion_placeholders(self):
		cases = (
			(
				"electric",
				"не применяется (ТС оборудовано электрической рулевой рейкой)",
				"-",
			),
			(
				"hydraulic",
				"соответствует",
				"Соответствует требованиям\nТР ТС 018/2011\nПриложения N 8 п.2.6",
			),
		)

		for booster_type, expected_status, expected_conclusion in cases:
			with self.subTest(steering_booster_type=booster_type):
				protocol = SimpleNamespace()
				measurement = SimpleNamespace(steering_booster_type=booster_type)
				light = SimpleNamespace()
				context = build_dynamic_result_values(protocol, measurement, light)
				applicability = build_applicability_values(
					protocol,
					measurement,
					light,
					context,
				)

				self.assertEqual(context["result_a_24_6_status"], expected_status)
				self.assertEqual(
					context["result_a_24_6_conclusion"],
					expected_conclusion,
				)
				self.assertEqual(applicability["applicable_24_6"], expected_status)

	def test_a26_7_uses_pneumatic_suspension_presence(self):
		protocol = SimpleNamespace()
		cases = (
			(
				False,
				"не применяется (на ТС отсутствует пневматическая подвеска)",
				"-",
			),
			(
				True,
				"соответствует",
				"Соответствует требованиям\nТР ТС 018/2011\nПриложения N 8 п.10.7",
			),
		)

		for present, expected_status, expected_conclusion in cases:
			with self.subTest(pneumatic_suspension_present=present):
				measurement = SimpleNamespace(
					pneumatic_suspension_present=present,
				)
				context = build_dynamic_result_values(
					protocol,
					measurement,
					SimpleNamespace(),
				)
				applicability = build_applicability_values(
					protocol,
					measurement,
					SimpleNamespace(),
					context,
				)

				self.assertEqual(context["result_a_26_7_status"], expected_status)
				self.assertEqual(context["result_a_26_7_conclusion"], expected_conclusion)
				self.assertEqual(applicability["applicable_26_7"], expected_status)

	def test_a20_5_2_depends_only_on_electric_engine(self):
		cases = (
			(
				"electric",
				"structural_elements",
				"не применяется (ТС оборудовано только электродвигателем)",
			),
			(
				"petrol",
				"structural_elements",
				"не применяется (на ТС отсутствуют элементы конструкции, "
				"не допускающие утечки избыточных паров и топлива в случае "
				"отсутствия крышки наливной горловины)",
			),
			(
				"diesel",
				"fixed_cap",
				"не применяется (на ТС отсутствуют элементы конструкции, "
				"не допускающие утечки избыточных паров и топлива в случае "
				"отсутствия крышки наливной горловины)",
			),
		)

		for fuel_type, protection_measure, expected in cases:
			with self.subTest(fuel_type=fuel_type, protection_measure=protection_measure):
				values = build_applicability_values(
					SimpleNamespace(),
					SimpleNamespace(
						fuel_type=fuel_type,
						fuel_tank_leak_protection_measure=protection_measure,
					),
					SimpleNamespace(),
					{},
				)

				self.assertEqual(values["applicable_20_5_2"], expected)

	def test_full_result_fields_use_excel_reasons(self):
		self.assertEqual(
			build_front_fog_values(SimpleNamespace(front_fog_count=0))[
				"full_result_a_8_10_1"
			],
			"не применяется (в ТС отсутствуют передние противотуманные фары)",
		)
		self.assertEqual(
			build_rear_fog_values(SimpleNamespace(rear_fog_count=0))[
				"full_result_a_8_13_2"
			],
			"не применяется (в ТС отсутствуют задние противотуманные фонари)",
		)
		self.assertEqual(
			build_tire_depth_values(
				SimpleNamespace(tire_season="summer"),
				SimpleNamespace(),
			)["full_result_a_10_7_3"],
			"не применяется (на ТС установлены летние шины)",
		)


	def test_front_fog_absence_marks_all_three_clauses_not_applicable(self):
		expected = "не применяется (в ТС отсутствуют передние противотуманные фары)"

		for count in (None, 0):
			with self.subTest(front_fog_count=count):
				protocol = SimpleNamespace()
				measurement = SimpleNamespace()
				light = SimpleNamespace(front_fog_count=count)
				context = build_front_fog_values(light)
				context.update(build_dynamic_result_values(protocol, measurement, light))

				values = build_applicability_values(
					protocol,
					measurement,
					light,
					context,
				)

				for clause in ("8_10_1", "8_10_2", "8_10_3"):
					self.assertEqual(values[f"applicable_{clause}"], expected)

	def test_optional_lights_mark_all_screenshot_clauses_not_applicable(self):
		expected_front_fog = (
			"не применяется (в ТС отсутствуют передние противотуманные фары)"
		)
		expected_rear_fog = (
			"не применяется (в ТС отсутствуют задние противотуманные фонари)"
		)
		protocol = SimpleNamespace()
		measurement = SimpleNamespace()

		for absent_count in (None, 0):
			with self.subTest(absent_count=absent_count):
				light = SimpleNamespace(
					front_fog_count=absent_count,
					rear_fog_count=absent_count,
					turn_signal_count=absent_count,
				)
				context = build_front_fog_values(light)
				context.update(build_rear_fog_values(light))
				context.update(build_dynamic_result_values(protocol, measurement, light))
				values = build_applicability_values(
					protocol,
					measurement,
					light,
					context,
				)

				for clause in ("8_10_1", "8_10_2", "8_10_3"):
					self.assertEqual(values[f"applicable_{clause}"], expected_front_fog)
				self.assertEqual(values["applicable_8_13_1"], expected_rear_fog)
				self.assertEqual(values["applicable_8_13_2"], expected_rear_fog)

	def test_eco_checks_apply_fuel_rules_and_inclusive_mileage_threshold(self):
		protocol = SimpleNamespace()
		cases = [
			("diesel", 1000, "не применяется (пробег ТС менее 3000 км)", "не применяется (пробег ТС менее 3000 км)"),
			("electric", 5000, "не применяется (ТС оборудовано только электродвигателем)", "не применяется (ТС оборудовано только электродвигателем)"),
			("petrol", 2999, "не применяется (пробег ТС менее 3000 км)", "не применяется (пробег ТС менее 3000 км)"),
			("petrol", 3000, "соответствует", "не применяется (ТС оборудовано бензиновым двигателем)"),
			("diesel", 3000, "не применяется (ТС оборудовано дизельным двигателем)", "соответствует"),
			("hybrid", 3000, "соответствует", "не применяется (ТС оборудовано бензиновым двигателем)"),
			(None, None, "соответствует", "соответствует"),
		]

		for fuel_type, mileage, co_status, smoke_status in cases:
			with self.subTest(fuel_type=fuel_type, mileage=mileage):
				measurement = SimpleNamespace(fuel_type=fuel_type, mileage_km=mileage)
				values = build_dynamic_result_values(
					protocol,
					measurement,
					SimpleNamespace(),
				)
				eco_values = build_eco_values(protocol, measurement)

				self.assertEqual(values["result_a_21_7_status"], co_status)
				self.assertEqual(values["result_a_21_8_status"], smoke_status)
				self.assertEqual(
					eco_values["a_21_7_low_mileage"],
					mileage is not None and mileage < 3000,
				)
				self.assertEqual(
					eco_values["a_21_7_numeric"],
					co_status == "соответствует",
				)
				self.assertEqual(
					eco_values["a_21_8_low_mileage"],
					mileage is not None and mileage < 3000,
				)
				self.assertEqual(
					eco_values["a_21_8_numeric"],
					smoke_status == "соответствует",
				)
				self.assertEqual(
					eco_values["mileage_21_9"],
					"не применяется (ТС оборудовано только электродвигателем)"
					if fuel_type == "electric"
					else "более 3000 км"
					if mileage is None or mileage >= 3000
					else "менее 3000 км",
				)
				if fuel_type is None and mileage is None:
					self.assertNotEqual(eco_values["full_result_a_21_9"], "-")
				self.assertEqual(
					values["result_a_21_9_status"],
					"не применяется (ТС оборудовано только электродвигателем)"
					if fuel_type == "electric"
					else "более 3000 км"
					if mileage is None or mileage >= 3000
					else "менее 3000 км",
				)


class ProtocolNumericRangeTests(SimpleTestCase):
	def test_condition_serializer_reports_label_and_bounds(self):
		serializer = ProtocolTestConditionSerializer(
			data={"ambient_temperature_c": "22.1"},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		message = str(serializer.errors["ambient_temperature_c"][0])
		self.assertIn("Температура окружающей среды", message)
		self.assertIn("18", message)
		self.assertIn("22", message)
		self.assertIn("°C", message)

	def test_explicit_dash_or_empty_value_skips_range_check(self):
		serializer = ProtocolTestConditionSerializer(
			data={
				"ambient_temperature_c": None,
				"dash_fields": ["ambient_temperature_c"],
			},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)

	def test_power_supply_uses_excel_voltage_limits(self):
		serializer = ProtocolPowerSupplySerializer(
			data={"phase_a_n_voltage_v": "186.99"},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn("phase_a_n_voltage_v", serializer.errors)
		self.assertIn("187", str(serializer.errors["phase_a_n_voltage_v"][0]))
		self.assertIn("242", str(serializer.errors["phase_a_n_voltage_v"][0]))

	def test_brake_difference_limit_depends_on_mechanism(self):
		disc = ProtocolBrakeSerializer(
			data={"service_brake_type": "disc_disc", "axle_1_brake_difference_pct": "20.1"},
			partial=True,
		)
		drum = ProtocolBrakeSerializer(
			data={"service_brake_type": "disc_drum", "axle_2_brake_difference_pct": "25"},
			partial=True,
		)

		self.assertFalse(disc.is_valid())
		self.assertIn("20", str(disc.errors["axle_1_brake_difference_pct"][0]))
		self.assertTrue(drum.is_valid(), drum.errors)

	def test_actual_speed_must_be_below_speedometer(self):
		serializer = ProtocolMeasurementSerializer(
			data={"actual_speed_kmh": "20", "speed_by_speedometer_kmh": "20"},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		self.assertIn("speed_by_speedometer_kmh", serializer.errors)
		self.assertIn("21", str(serializer.errors["speed_by_speedometer_kmh"][0]))

	def test_non_headlight_light_count_uses_allowed_discrete_values(self):
		serializer = ProtocolLightSerializer(
			data={"reverse_light_count": 3},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		message = str(serializer.errors["reverse_light_count"][0])
		self.assertIn("1 или 2", message)
		self.assertIn("от 1 до 2", message)

	def test_turn_signal_frequency_only_accepts_excel_values(self):
		serializer = ProtocolLightSerializer(
			data={"turn_signal_frequency_hz": "1.5"},
			partial=True,
		)

		self.assertFalse(serializer.is_valid())
		message = str(serializer.errors["turn_signal_frequency_hz"][0])
		self.assertIn("1,4 или 1,6", message)

	def test_headlight_values_are_not_range_restricted(self):
		serializer = ProtocolLightSerializer(
			data={"low_beam_count": 4, "front_fog_count": 3, "left_high_beam_cd": "200000"},
			partial=True,
		)

		self.assertTrue(serializer.is_valid(), serializer.errors)


class ProtocolCalculationTests(TestCase):
	def test_light_absorption_uncertainty_uses_type_b_for_equal_readings(self):
		measurement = SimpleNamespace(
			light_absorption_1=Decimal("0.10"),
			light_absorption_2=Decimal("0.10"),
			light_absorption_3=Decimal("0.10"),
			light_absorption_4=Decimal("0.10"),
			light_absorption_5=Decimal("0.10"),
			light_absorption_6=Decimal("0.10"),
		)

		uncertainty = calc_light_absorption_uncertainty(measurement)

		self.assertAlmostEqual(float(uncertainty), 0.0476338, places=6)

	def test_light_absorption_uncertainty_increases_with_reading_spread(self):
		stable = SimpleNamespace(**{
			f"light_absorption_{index}": Decimal("0.10")
			for index in range(1, 7)
		})
		spread = SimpleNamespace(
			light_absorption_1=Decimal("0.00"),
			light_absorption_2=Decimal("0.02"),
			light_absorption_3=Decimal("0.10"),
			light_absorption_4=Decimal("0.12"),
			light_absorption_5=Decimal("0.20"),
			light_absorption_6=Decimal("0.22"),
		)

		self.assertGreater(
			calc_light_absorption_uncertainty(spread),
			calc_light_absorption_uncertainty(stable),
		)

	def test_headlight_uncertainty_includes_resolution_component(self):
		relative_only = Decimal("450") * Decimal("15") / Decimal("100") / Decimal("3").sqrt()
		updated = standard_headlight_uncertainty_cd(Decimal("450"))

		self.assertGreater(updated, relative_only)

	def test_control_force_uncertainty_includes_resolution_component(self):
		relative_only = Decimal("98") * Decimal("5") / Decimal("100") / Decimal("3").sqrt()

		self.assertGreater(
			u_control_force_n(Decimal("98")),
			Decimal("1.65") * relative_only,
		)

	def test_turn_signal_frequency_uncertainty_includes_resolution_component(self):
		old_relative_only = Decimal("1.65") * Decimal("0.1") / Decimal("3").sqrt()

		self.assertGreater(u_turn_signal_frequency_hz(), old_relative_only)

	def test_measurement_uncertainties_include_resolution_components(self):
		old_noise = Decimal("1.65") * Decimal("0.5") / Decimal("3").sqrt()
		old_glass = Decimal("1.65") * Decimal("2") / Decimal("3").sqrt()
		old_speed = Decimal("1.65") * Decimal("20") * Decimal("0.15") / Decimal("100") / Decimal("3").sqrt()

		self.assertGreater(u_noise_db(), old_noise)
		self.assertGreater(u_glass_transparency_pct(), old_glass)
		self.assertGreater(u_speed_kmh(Decimal("20")), old_speed)

	def test_scale_uncertainty_includes_resolution_component(self):
		old_scale = Decimal("1.65") * Decimal("5") / Decimal("3").sqrt()

		self.assertGreater(u_scale_kg(), old_scale)

	def test_steering_and_height_uncertainties_use_new_instrument_components(self):
		old_steering = Decimal("1.65") * Decimal("0.5") / Decimal("3").sqrt()
		old_height = Decimal("1.65") * Decimal("0.3") / Decimal("3").sqrt()

		self.assertGreater(u_steering_backlash_deg(), old_steering)
		self.assertNotEqual(u_vehicle_height_mm(1640), old_height)


class ProtocolDocxConditionalRowTests(SimpleTestCase):
	def test_table_row_else_renders_only_the_matching_branch(self):
		for condition, expected in ((True, "present"), (False, "absent")):
			with self.subTest(condition=condition):
				document = Document()
			table = document.add_table(rows=5, cols=1)
			table.cell(0, 0).text = "{%tr if front_fog_present %}"
			table.cell(1, 0).text = "present"
			table.cell(2, 0).text = "{%tr else %}"
			table.cell(3, 0).text = "absent"
			table.cell(4, 0).text = "{%tr endif %}"

			process_document_conditions(
				document,
				{"front_fog_present": condition},
			)

			self.assertEqual(
				[row.cells[0].text for row in document.tables[0].rows],
				[expected],
			)
