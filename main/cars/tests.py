from datetime import date
from decimal import Decimal
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone
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
	build_dynamic_result_values,
	build_eco_values,
	build_front_fog_values,
	build_rear_fog_values,
	build_tire_depth_values,
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
	def test_generator_selects_old_and_v4_templates(self):
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
					v4_output = generate_protocol_docx(protocol, "v4")

		self.assertEqual(old_output.name, "protocol_42_old.docx")
		self.assertEqual(v4_output.name, "protocol_42_v4.docx")
		self.assertEqual(
			[
				call.kwargs["template_path"].name
				for call in render.call_args_list
			],
			["protocol_template.docx", "protocol_template_v4_source.docx"],
		)

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
	def test_rear_fog_width_requirement_applies_only_to_one_lamp(self):
		protocol = SimpleNamespace()
		measurement = SimpleNamespace()
		cases = (
			(None, "не указано"),
			(0, "не применяется (в ТС отсутствуют задние противотуманные фонари)"),
			(1, "соответствует"),
			(2, "не применяется (в ТС имеется два задних противотуманных фонаря)"),
		)

		for count, expected in cases:
			with self.subTest(rear_fog_count=count):
				light = SimpleNamespace(rear_fog_count=count)
				values = build_dynamic_result_values(protocol, measurement, light)

				self.assertEqual(values["result_a_8_13_1_status"], expected)

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
			"не применяется (в ТС отсутствует адаптивная система переднего освещения)",
		)
		self.assertEqual(
			values["result_a_8_20_3_status"],
			"не применяется (ТС не оснащено устройствами фароочистки  и автоматическим корректирующим устройством угла наклона фар (не предусмотренно конструкцией))",
		)
		self.assertEqual(
			values["result_a_10_5_status"],
			"не применяется (на ТС установлены летние шины)",
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
			"не применяется (ТС оборудовано дизельным двигателем)",
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
		self.assertEqual(values["applicable_8_20_3"], "не указано")
		self.assertIn("applicable_21_8", values)
		self.assertFalse(any(key.startswith("not_applicable_") for key in values))

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

	def test_eco_checks_apply_fuel_rules_and_inclusive_mileage_threshold(self):
		protocol = SimpleNamespace()
		cases = [
			("diesel", 1000, "не применяется (ТС оборудовано дизельным двигателем)", "не применяется (пробег ТС менее 3000 км)"),
			("electric", 5000, "не применяется (ТС оборудовано только электродвигателем)", "не применяется (ТС оборудовано только электродвигателем)"),
			("petrol", 2999, "не применяется (пробег ТС менее 3000 км)", "не применяется (ТС оборудовано бензиновым двигателем)"),
			("petrol", 3000, "соответствует", "не применяется (ТС оборудовано бензиновым двигателем)"),
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
					eco_values["mileage_21_9"],
					"не применяется (ТС оборудовано только электродвигателем)"
					if fuel_type == "electric"
					else "не менее 3000 км"
					if mileage >= 3000
					else f"менее 3000 км",
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
