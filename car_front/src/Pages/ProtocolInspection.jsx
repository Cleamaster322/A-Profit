import {useEffect, useRef, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";
import api from "../shared/api.jsx";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Alert from "@mui/material/Alert";
import Chip from "@mui/material/Chip";

import ProtocolInspectionHeader from "../Features/ProtocolInspection/ProtocolInspectionHeader.jsx";
import ProtocolInspectionConditions from "../Features/ProtocolInspection/ProtocolInspectionConditions.jsx";
import ProtocolInspectionPhotos from "../Features/ProtocolInspection/ProtocolInspectionPhotos.jsx";
import ProtocolInspectionVehicle from "../Features/ProtocolInspection/ProtocolInspectionVehicle.jsx";
import ProtocolInspectionEngine from "../Features/ProtocolInspection/ProtocolInspectionEngine.jsx";
import ProtocolInspectionSteeringTransmission
    from "../Features/ProtocolInspection/ProtocolInspectionSteeringTransmission.jsx";
import ProtocolInspectionBrakes from "../Features/ProtocolInspection/ProtocolInspectionBrakes.jsx";
import ProtocolInspectionLightsMain from "../Features/ProtocolInspection/ProtocolInspectionLightsMain.jsx";
import ProtocolInspectionLightsGeometry from "../Features/ProtocolInspection/ProtocolInspectionLightsGeometry.jsx";
import ProtocolInspectionMisc from "../Features/ProtocolInspection/ProtocolInspectionMisc.jsx";
import AppHeader from "../Features/AppHeader/AppHeader.jsx";

import {
    pageSx,
    pageInnerSx,
    sectionPaperSx,
    sectionTitleSx,
    subsectionTitleSx,
    textFieldSx,
    selectFieldSx,
} from "../Features/ProtocolInspection/protocolInspectionStyles.jsx";

const initialForm = {
    protocol_number: "",
    appendix_number: "",
    protocol_date: "",
    status: "",
    owner_last_name: "",
    owner_first_name: "",
    owner_middle_name: "",
    manufacturer_info: "",

    ambient_temp_c: "",
    ambient_humidity_pct: "",
    atmospheric_pressure_kpa: "",
    road_ambient_temp_c: "",
    road_ambient_humidity_pct: "",
    electric_frequency_hz: "",
    voltage_phase_a_zero: "",
    voltage_phase_b_zero: "",
    voltage_phase_c_zero: "",
    voltage_phase_ab: "",
    voltage_phase_bc: "",
    voltage_phase_ac: "",

    photos_comment: "",

    brand_name: "",
    commercial_name: "",
    vin: "",
    category: "",
    body_type: "",
    mileage_km: "",
    tire_marking_front: "",
    tire_marking_rear: "",
    tire_season: "",
    tire_spikes_present: "",
    manufacture_year: "",
    color: "",
    wheel_formula: "",
    mufflers_count: "",
    seats_count: "",
    side_steps_present: "",

    engine_model: "",
    engine_power_kw: "",
    engine_layout: "",
    cylinder_layout: "",
    cylinders_count: "",
    fuel_type: "",
    turbo_present: "",

    steering_booster_type: "",
    steering_backlash_deg: "",
    transmission_type: "",

    service_brake_type: "",
    parking_brake_type: "",
    service_brake_control_force_axle1_n: "",
    service_brake_control_force_axle2_n: "",
    parking_brake_control_force_n: "",
    axle_1_brake_difference_pct: "",
    axle_2_brake_difference_pct: "",
    service_brake_front_left_kn: "",
    service_brake_front_right_kn: "",
    service_brake_rear_left_kn: "",
    service_brake_rear_right_kn: "",
    parking_brake_left_kn: "",
    parking_brake_right_kn: "",

    low_beam_count: "",
    low_beam_color: "",
    high_beam_count: "",
    high_beam_color: "",
    front_fog_count: "",
    front_fog_color: "",
    reverse_light_count: "",
    reverse_light_color: "",
    turn_signal_count: "",
    turn_signal_color: "",
    front_position_light_count: "",
    front_position_light_color: "",
    rear_position_light_count: "",
    rear_position_light_color: "",
    main_brake_signal_count: "",
    main_brake_signal_color: "",
    additional_brake_signal_count: "",
    additional_brake_signal_color: "",
    rear_fog_count: "",
    rear_fog_color: "",
    plate_light_count: "",
    plate_light_color: "",
    daytime_running_light_count: "",
    daytime_running_light_color: "",

    parking_light_count: "",
    parking_light_color: "",
    rear_parking_light_count: "",
    rear_parking_light_color: "",
    adaptive_front_lighting_count: "",
    adaptive_front_lighting_color: "",

    headlight_type: "",
    headlight_washer_present: "",
    left_34v_cd: "",
    left_52h_cd: "",
    left_high_beam_cd: "",
    right_34v_cd: "",
    right_52h_cd: "",
    right_high_beam_cd: "",
    turn_signal_frequency_per_min: "",
    turn_signal_frequency_hz: "",

    low_beam_upper_point_mm: "",
    low_beam_lower_point_mm: "",
    fog_light_upper_point_mm: "",
    fog_light_lower_point_mm: "",
    fog_light_left_distance_mm: "",
    fog_light_right_distance_mm: "",
    brake_signal_upper_point_mm: "",
    brake_signal_lower_point_mm: "",
    brake_signal_left_distance_mm: "",
    brake_signal_right_distance_mm: "",
    additional_brake_signal_from_glass_edge_mm: "",
    additional_brake_signal_from_support_surface_mm: "",
    additional_brake_signal_optical_center_shift_mm: "",
    rear_fog_upper_point_mm: "",
    rear_fog_lower_point_mm: "",

    spare_wheel_present: "",
    steering_lock_present: "",
    gas_equipment_present: "",
    glonass_button_present: "",

    bumper_ends_bent_to_body: "",
    bumper_to_body_distance_mm: "",
    opening_roof_present: "",
    fuel_leak_prevention_measure: "",
    protruding_elements_doors_mm: "",
    protruding_elements_other_mm: "",
    glass_transparency_right_pct: "",
    glass_transparency_left_pct: "",
    glass_transparency_windshield_pct: "",
    sun_strip_width_mm: "",
    speed_by_speedometer_kmh: "",
    actual_speed_kmh: "",
    exhaust_noise_constant_db: "",
    exhaust_noise_deceleration_db: "",
    co_min_pct: "",
    co_max_pct: "",
    light_absorption_1: "",
    light_absorption_2: "",
    light_absorption_3: "",
    light_absorption_4: "",
    light_absorption_5: "",
    light_absorption_6: "",
    vehicle_length_mm: "",
    vehicle_width_mm: "",
    vehicle_height_mm: "",
    vehicle_weight_kg: "",
    axle1_load_kg: "",
    axle2_load_kg: "",

    tire_depth_fl_mm: "",
    tire_depth_rl_mm: "",
    tire_depth_fr_mm: "",
    tire_depth_rr_mm: "",
};

function isDashValue(value) {
    return typeof value === "string" && value.trim() === "-";
}

function toFormValue(value, dashFields = [], apiFieldName = null) {
    if (value === null || value === undefined) {
        if (
            apiFieldName &&
            Array.isArray(dashFields) &&
            dashFields.includes(apiFieldName)
        ) {
            return "-";
        }

        return "";
    }

    return value;
}

function booleanToSelect(value) {
    if (value === true) return "true";
    if (value === false) return "false";
    return "";
}

function emptyToNull(value) {
    if (value === null || value === undefined) {
        return null;
    }

    if (typeof value === "string") {
        const trimmedValue = value.trim();

        if (trimmedValue === "" || trimmedValue === "-") {
            return null;
        }

        return trimmedValue;
    }

    return value;
}

function normalizeDecimalComma(value) {
    if (typeof value !== "string") {
        return value;
    }

    const trimmedValue = value.trim();

    if (trimmedValue === "" || trimmedValue === "-") {
        return value;
    }

    return trimmedValue.replace(",", ".");
}

function normalizeNumericPayload(payload, numericFields) {
    const normalizedPayload = {
        ...payload,
    };

    numericFields.forEach((fieldName) => {
        if (fieldName in normalizedPayload) {
            normalizedPayload[fieldName] = normalizeDecimalComma(
                normalizedPayload[fieldName]
            );
        }
    });

    return normalizedPayload;
}

function formatProtocolNumber(value) {
    if (value === null || value === undefined) {
        return null;
    }

    const digits = String(value).replace(/\D/g, "");

    if (!digits) {
        return null;
    }

    return digits.padStart(5, "0");
}

function stringToBooleanOrNull(value) {
    if (value === "true") return true;
    if (value === "false") return false;
    return null;
}

function buildDashFields(form, fieldMap) {
    return fieldMap
        .filter(({formField}) => isDashValue(form[formField]))
        .map(({apiField}) => apiField);
}

function formatDateForChip(value) {
    if (!value) {
        return "не указана";
    }

    const parts = String(value).split("-");

    if (parts.length !== 3) {
        return value;
    }

    const [year, month, day] = parts;

    return `${day}-${month}-${year}`;
}

function formatApiError(errorData) {
    if (!errorData) {
        return "Ошибка сохранения блока";
    }

    if (typeof errorData === "string") {
        return errorData;
    }

    if (Array.isArray(errorData)) {
        return errorData.join(", ");
    }

    if (typeof errorData === "object") {
        return Object.entries(errorData)
            .map(([field, messages]) => {
                if (Array.isArray(messages)) {
                    return `${field}: ${messages.join(", ")}`;
                }

                return `${field}: ${messages}`;
            })
            .join("\n");
    }

    return "Ошибка сохранения блока";
}

function getErrorFields(errorData) {
    if (!errorData || typeof errorData !== "object" || Array.isArray(errorData)) {
        return [];
    }

    return Object.keys(errorData);
}

function hasAnyField(errorFields, expectedFields) {
    return errorFields.some((field) => expectedFields.includes(field));
}

function BlockError({message}) {
    if (!message) {
        return null;
    }

    return (
        <Alert
            severity="error"
            sx={{
                mb: 2,
                borderRadius: 0,
                border: "1px solid #b3261e",
                whiteSpace: "pre-line",
            }}
        >
            {message}
        </Alert>
    );
}

const PROTOCOL_DASH_FIELDS = [
    {formField: "protocol_number", apiField: "protocol_number"},
    {formField: "appendix_number", apiField: "appendix_number"},
    {formField: "owner_last_name", apiField: "owner_last_name"},
    {formField: "owner_first_name", apiField: "owner_first_name"},
    {formField: "owner_middle_name", apiField: "owner_middle_name"},
    {formField: "manufacturer_info", apiField: "manufacturer_info"},
    {formField: "brand_name", apiField: "brand_name"},
    {formField: "commercial_name", apiField: "commercial_name"},
    {formField: "vin", apiField: "vin"},
    {formField: "category", apiField: "vehicle_category"},
    {formField: "body_type", apiField: "body_type"},
    {formField: "tire_marking_front", apiField: "wheel_marking_front"},
    {formField: "tire_marking_rear", apiField: "wheel_marking_rear"},
    {formField: "tire_season", apiField: "tire_season"},
    {formField: "manufacture_year", apiField: "manufacture_year"},
    {formField: "color", apiField: "color"},
];

const TEST_CONDITIONS_DASH_FIELDS = [
    {formField: "ambient_temp_c", apiField: "ambient_temperature_c"},
    {formField: "ambient_humidity_pct", apiField: "relative_humidity_pct"},
    {formField: "atmospheric_pressure_kpa", apiField: "atmospheric_pressure_kpa"},
];

const ROAD_CONDITIONS_DASH_FIELDS = [
    {formField: "road_ambient_temp_c", apiField: "road_ambient_temperature_c"},
    {formField: "road_ambient_humidity_pct", apiField: "road_relative_humidity_pct"},
];

const POWER_SUPPLY_DASH_FIELDS = [
    {formField: "electric_frequency_hz", apiField: "frequency_hz"},
    {formField: "voltage_phase_a_zero", apiField: "phase_a_n_voltage_v"},
    {formField: "voltage_phase_b_zero", apiField: "phase_b_n_voltage_v"},
    {formField: "voltage_phase_c_zero", apiField: "phase_c_n_voltage_v"},
    {formField: "voltage_phase_ab", apiField: "phase_ab_voltage_v"},
    {formField: "voltage_phase_bc", apiField: "phase_bc_voltage_v"},
    {formField: "voltage_phase_ac", apiField: "phase_ac_voltage_v"},
];

const MEASUREMENT_DASH_FIELDS = [
    {formField: "mileage_km", apiField: "mileage_km"},

    {formField: "wheel_formula", apiField: "wheel_formula"},
    {formField: "mufflers_count", apiField: "mufflers_count"},
    {formField: "seats_count", apiField: "seats_count"},

    {formField: "engine_model", apiField: "engine_model"},
    {formField: "engine_power_kw", apiField: "engine_power_kw"},
    {formField: "engine_layout", apiField: "engine_layout"},
    {formField: "cylinder_layout", apiField: "cylinder_layout"},
    {formField: "cylinders_count", apiField: "cylinders_count"},
    {formField: "fuel_type", apiField: "fuel_type"},

    {formField: "steering_booster_type", apiField: "steering_booster_type"},
    {formField: "steering_backlash_deg", apiField: "steering_backlash_deg"},
    {formField: "transmission_type", apiField: "transmission_type"},

    {formField: "tire_depth_fl_mm", apiField: "tire_depth_fl_mm"},
    {formField: "tire_depth_fr_mm", apiField: "tire_depth_fr_mm"},
    {formField: "tire_depth_rl_mm", apiField: "tire_depth_rl_mm"},
    {formField: "tire_depth_rr_mm", apiField: "tire_depth_rr_mm"},

    {formField: "bumper_to_body_distance_mm", apiField: "bumper_to_body_distance_mm"},
    {formField: "fuel_leak_prevention_measure", apiField: "fuel_tank_leak_protection_measure"},
    {formField: "protruding_elements_doors_mm", apiField: "protruding_elements_doors_mm"},
    {formField: "protruding_elements_other_mm", apiField: "protruding_elements_other_mm"},

    {formField: "glass_transparency_right_pct", apiField: "glass_transparency_right_pct"},
    {formField: "glass_transparency_left_pct", apiField: "glass_transparency_left_pct"},
    {formField: "glass_transparency_windshield_pct", apiField: "glass_transparency_windshield_pct"},
    {formField: "sun_strip_width_mm", apiField: "sun_strip_width_mm"},

    {formField: "speed_by_speedometer_kmh", apiField: "speed_by_speedometer_kmh"},
    {formField: "actual_speed_kmh", apiField: "actual_speed_kmh"},

    {formField: "exhaust_noise_constant_db", apiField: "exhaust_noise_constant_db"},
    {formField: "exhaust_noise_deceleration_db", apiField: "exhaust_noise_deceleration_db"},
    {formField: "co_min_pct", apiField: "co_min_pct"},
    {formField: "co_max_pct", apiField: "co_max_pct"},

    {formField: "light_absorption_1", apiField: "light_absorption_1"},
    {formField: "light_absorption_2", apiField: "light_absorption_2"},
    {formField: "light_absorption_3", apiField: "light_absorption_3"},
    {formField: "light_absorption_4", apiField: "light_absorption_4"},
    {formField: "light_absorption_5", apiField: "light_absorption_5"},
    {formField: "light_absorption_6", apiField: "light_absorption_6"},

    {formField: "vehicle_length_mm", apiField: "vehicle_length_mm"},
    {formField: "vehicle_width_mm", apiField: "vehicle_width_mm"},
    {formField: "vehicle_height_mm", apiField: "vehicle_height_mm"},
    {formField: "vehicle_weight_kg", apiField: "vehicle_weight_kg"},

    {formField: "axle1_load_kg", apiField: "axle1_load_kg"},
    {formField: "axle2_load_kg", apiField: "axle2_load_kg"},
];

const BRAKE_DASH_FIELDS = [
    {formField: "service_brake_type", apiField: "service_brake_type"},
    {formField: "parking_brake_type", apiField: "parking_brake_type"},

    {formField: "service_brake_control_force_axle1_n", apiField: "service_brake_control_force_axle1_n"},
    {formField: "service_brake_control_force_axle2_n", apiField: "service_brake_control_force_axle2_n"},
    {formField: "parking_brake_control_force_n", apiField: "parking_brake_control_force_n"},

    {formField: "axle_1_brake_difference_pct", apiField: "axle_1_brake_difference_pct"},
    {formField: "axle_2_brake_difference_pct", apiField: "axle_2_brake_difference_pct"},

    {formField: "service_brake_front_left_kn", apiField: "service_brake_front_left_kn"},
    {formField: "service_brake_front_right_kn", apiField: "service_brake_front_right_kn"},
    {formField: "service_brake_rear_left_kn", apiField: "service_brake_rear_left_kn"},
    {formField: "service_brake_rear_right_kn", apiField: "service_brake_rear_right_kn"},

    {formField: "parking_brake_left_kn", apiField: "parking_brake_left_kn"},
    {formField: "parking_brake_right_kn", apiField: "parking_brake_right_kn"},
];

const LIGHT_DASH_FIELDS = [
    {formField: "low_beam_count", apiField: "low_beam_count"},
    {formField: "low_beam_color", apiField: "low_beam_color"},
    {formField: "high_beam_count", apiField: "high_beam_count"},
    {formField: "high_beam_color", apiField: "high_beam_color"},
    {formField: "front_fog_count", apiField: "front_fog_count"},
    {formField: "front_fog_color", apiField: "front_fog_color"},
    {formField: "reverse_light_count", apiField: "reverse_light_count"},
    {formField: "reverse_light_color", apiField: "reverse_light_color"},
    {formField: "turn_signal_count", apiField: "turn_signal_count"},
    {formField: "turn_signal_color", apiField: "turn_signal_color"},
    {formField: "front_position_light_count", apiField: "front_position_light_count"},
    {formField: "front_position_light_color", apiField: "front_position_light_color"},
    {formField: "rear_position_light_count", apiField: "rear_position_light_count"},
    {formField: "rear_position_light_color", apiField: "rear_position_light_color"},
    {formField: "main_brake_signal_count", apiField: "main_brake_signal_count"},
    {formField: "main_brake_signal_color", apiField: "main_brake_signal_color"},
    {formField: "additional_brake_signal_count", apiField: "additional_brake_signal_count"},
    {formField: "additional_brake_signal_color", apiField: "additional_brake_signal_color"},
    {formField: "rear_fog_count", apiField: "rear_fog_count"},
    {formField: "rear_fog_color", apiField: "rear_fog_color"},
    {formField: "plate_light_count", apiField: "plate_light_count"},
    {formField: "plate_light_color", apiField: "plate_light_color"},
    {formField: "daytime_running_light_count", apiField: "daytime_running_light_count"},
    {formField: "daytime_running_light_color", apiField: "daytime_running_light_color"},

    {formField: "parking_light_count", apiField: "parking_light_count"},
    {formField: "parking_light_color", apiField: "parking_light_color"},
    {formField: "rear_parking_light_count", apiField: "rear_parking_light_count"},
    {formField: "rear_parking_light_color", apiField: "rear_parking_light_color"},
    {formField: "adaptive_front_lighting_count", apiField: "adaptive_front_lighting_count"},
    {formField: "adaptive_front_lighting_color", apiField: "adaptive_front_lighting_color"},

    {formField: "headlight_type", apiField: "headlight_type"},

    {formField: "left_34v_cd", apiField: "left_34v_cd"},
    {formField: "left_52h_cd", apiField: "left_52h_cd"},
    {formField: "left_high_beam_cd", apiField: "left_high_beam_cd"},
    {formField: "right_34v_cd", apiField: "right_34v_cd"},
    {formField: "right_52h_cd", apiField: "right_52h_cd"},
    {formField: "right_high_beam_cd", apiField: "right_high_beam_cd"},
    {formField: "turn_signal_frequency_per_min", apiField: "turn_signal_frequency_per_min"},
    {formField: "turn_signal_frequency_hz", apiField: "turn_signal_frequency_hz"},

    {formField: "low_beam_upper_point_mm", apiField: "low_beam_upper_point_mm"},
    {formField: "low_beam_lower_point_mm", apiField: "low_beam_lower_point_mm"},
    {formField: "fog_light_upper_point_mm", apiField: "fog_light_upper_point_mm"},
    {formField: "fog_light_lower_point_mm", apiField: "fog_light_lower_point_mm"},
    {formField: "fog_light_left_distance_mm", apiField: "fog_light_left_distance_mm"},
    {formField: "fog_light_right_distance_mm", apiField: "fog_light_right_distance_mm"},
    {formField: "brake_signal_upper_point_mm", apiField: "brake_signal_upper_point_mm"},
    {formField: "brake_signal_lower_point_mm", apiField: "brake_signal_lower_point_mm"},
    {formField: "brake_signal_left_distance_mm", apiField: "brake_signal_left_distance_mm"},
    {formField: "brake_signal_right_distance_mm", apiField: "brake_signal_right_distance_mm"},
    {formField: "additional_brake_signal_from_glass_edge_mm", apiField: "additional_brake_signal_from_glass_edge_mm"},
    {
        formField: "additional_brake_signal_from_support_surface_mm",
        apiField: "additional_brake_signal_from_support_surface_mm",
    },
    {
        formField: "additional_brake_signal_optical_center_shift_mm",
        apiField: "additional_brake_signal_optical_center_shift_mm",
    },
    {formField: "rear_fog_upper_point_mm", apiField: "rear_fog_upper_point_mm"},
    {formField: "rear_fog_lower_point_mm", apiField: "rear_fog_lower_point_mm"},
];

const MEASUREMENT_ENGINE_FIELDS = [
    "engine_model",
    "engine_power_kw",
    "engine_layout",
    "cylinder_layout",
    "cylinders_count",
    "fuel_type",
    "turbo_present",
];

const MEASUREMENT_STEERING_TRANSMISSION_FIELDS = [
    "steering_booster_type",
    "steering_backlash_deg",
    "transmission_type",
];

const MEASUREMENT_MISC_FIELDS = [
    "tire_depth_fl_mm",
    "tire_depth_fr_mm",
    "tire_depth_rl_mm",
    "tire_depth_rr_mm",
    "bumper_bends_to_body",
    "bumper_to_body_distance_mm",
    "opening_roof_present",
    "fuel_tank_leak_protection_measure",
    "protruding_elements_doors_mm",
    "protruding_elements_other_mm",
    "glass_transparency_right_pct",
    "glass_transparency_left_pct",
    "glass_transparency_windshield_pct",
    "sun_strip_width_mm",
    "speed_by_speedometer_kmh",
    "actual_speed_kmh",
    "exhaust_noise_constant_db",
    "exhaust_noise_deceleration_db",
    "co_min_pct",
    "co_max_pct",
    "light_absorption_1",
    "light_absorption_2",
    "light_absorption_3",
    "light_absorption_4",
    "light_absorption_5",
    "light_absorption_6",
    "vehicle_length_mm",
    "vehicle_width_mm",
    "vehicle_height_mm",
    "vehicle_weight_kg",
    "axle1_load_kg",
    "axle2_load_kg",
    "spare_wheel_present",
    "steering_lock_present",
    "gas_equipment_present",
    "glonass_button_present",
];

const LIGHT_GEOMETRY_FIELDS = [
    "low_beam_upper_point_mm",
    "low_beam_lower_point_mm",
    "fog_light_upper_point_mm",
    "fog_light_lower_point_mm",
    "fog_light_left_distance_mm",
    "fog_light_right_distance_mm",
    "brake_signal_upper_point_mm",
    "brake_signal_lower_point_mm",
    "brake_signal_left_distance_mm",
    "brake_signal_right_distance_mm",
    "additional_brake_signal_from_glass_edge_mm",
    "additional_brake_signal_from_support_surface_mm",
    "additional_brake_signal_optical_center_shift_mm",
    "rear_fog_upper_point_mm",
    "rear_fog_lower_point_mm",
];

const PROTOCOL_NUMERIC_FIELDS = [
    "manufacture_year",
];

const TEST_CONDITIONS_NUMERIC_FIELDS = [
    "ambient_temperature_c",
    "relative_humidity_pct",
    "atmospheric_pressure_kpa",
];

const ROAD_CONDITIONS_NUMERIC_FIELDS = [
    "road_ambient_temperature_c",
    "road_relative_humidity_pct",
];

const POWER_SUPPLY_NUMERIC_FIELDS = [
    "frequency_hz",
    "phase_a_n_voltage_v",
    "phase_b_n_voltage_v",
    "phase_c_n_voltage_v",
    "phase_ab_voltage_v",
    "phase_bc_voltage_v",
    "phase_ac_voltage_v",
];

const MEASUREMENT_NUMERIC_FIELDS = [
    "mileage_km",
    "mufflers_count",

    "engine_power_kw",
    "cylinders_count",

    "steering_backlash_deg",

    "tire_depth_fl_mm",
    "tire_depth_fr_mm",
    "tire_depth_rl_mm",
    "tire_depth_rr_mm",

    "bumper_to_body_distance_mm",
    "protruding_elements_doors_mm",
    "protruding_elements_other_mm",

    "glass_transparency_right_pct",
    "glass_transparency_left_pct",
    "glass_transparency_windshield_pct",
    "sun_strip_width_mm",

    "speed_by_speedometer_kmh",
    "actual_speed_kmh",

    "exhaust_noise_constant_db",
    "exhaust_noise_deceleration_db",

    "co_min_pct",
    "co_max_pct",

    "light_absorption_1",
    "light_absorption_2",
    "light_absorption_3",
    "light_absorption_4",
    "light_absorption_5",
    "light_absorption_6",

    "vehicle_length_mm",
    "vehicle_width_mm",
    "vehicle_height_mm",
    "vehicle_weight_kg",

    "axle1_load_kg",
    "axle2_load_kg",
];

const BRAKE_NUMERIC_FIELDS = [
    "service_brake_control_force_axle1_n",
    "service_brake_control_force_axle2_n",
    "parking_brake_control_force_n",

    "axle_1_brake_difference_pct",
    "axle_2_brake_difference_pct",

    "service_brake_front_left_kn",
    "service_brake_front_right_kn",
    "service_brake_rear_left_kn",
    "service_brake_rear_right_kn",

    "parking_brake_left_kn",
    "parking_brake_right_kn",
];

const LIGHT_NUMERIC_FIELDS = [
    "low_beam_count",
    "high_beam_count",
    "front_fog_count",
    "reverse_light_count",
    "turn_signal_count",
    "front_position_light_count",
    "rear_position_light_count",
    "main_brake_signal_count",
    "additional_brake_signal_count",
    "rear_fog_count",
    "plate_light_count",
    "daytime_running_light_count",
    "parking_light_count",
    "rear_parking_light_count",
    "adaptive_front_lighting_count",

    "left_34v_cd",
    "left_52h_cd",
    "left_high_beam_cd",
    "right_34v_cd",
    "right_52h_cd",
    "right_high_beam_cd",

    "turn_signal_frequency_per_min",
    "turn_signal_frequency_hz",

    "low_beam_upper_point_mm",
    "low_beam_lower_point_mm",

    "fog_light_upper_point_mm",
    "fog_light_lower_point_mm",
    "fog_light_left_distance_mm",
    "fog_light_right_distance_mm",

    "brake_signal_upper_point_mm",
    "brake_signal_lower_point_mm",
    "brake_signal_left_distance_mm",
    "brake_signal_right_distance_mm",

    "additional_brake_signal_from_glass_edge_mm",
    "additional_brake_signal_from_support_surface_mm",
    "additional_brake_signal_optical_center_shift_mm",

    "rear_fog_upper_point_mm",
    "rear_fog_lower_point_mm",
];

function mapProtocolToForm(data) {
    const protocol = data || {};
    const measurement = protocol.measurement || {};
    const brake = protocol.brake || {};
    const light = protocol.light || {};
    const testConditions = protocol.test_conditions || {};
    const roadConditions = protocol.road_conditions || {};
    const powerSupply = protocol.power_supply || {};

    const protocolDashFields = protocol.dash_fields || [];
    const measurementDashFields = measurement.dash_fields || [];
    const brakeDashFields = brake.dash_fields || [];
    const lightDashFields = light.dash_fields || [];
    const testConditionsDashFields = testConditions.dash_fields || [];
    const roadConditionsDashFields = roadConditions.dash_fields || [];
    const powerSupplyDashFields = powerSupply.dash_fields || [];

    return {
        ...initialForm,

        protocol_number: toFormValue(protocol.protocol_number, protocolDashFields, "protocol_number"),
        appendix_number: toFormValue(protocol.appendix_number, protocolDashFields, "appendix_number"),
        protocol_date: protocol.protocol_date || "",
        status: protocol.status || "",

        owner_last_name: toFormValue(protocol.owner_last_name, protocolDashFields, "owner_last_name"),
        owner_first_name: toFormValue(protocol.owner_first_name, protocolDashFields, "owner_first_name"),
        owner_middle_name: toFormValue(protocol.owner_middle_name, protocolDashFields, "owner_middle_name"),
        manufacturer_info: toFormValue(protocol.manufacturer_info, protocolDashFields, "manufacturer_info"),

        ambient_temp_c: toFormValue(testConditions.ambient_temperature_c, testConditionsDashFields, "ambient_temperature_c"),
        ambient_humidity_pct: toFormValue(testConditions.relative_humidity_pct, testConditionsDashFields, "relative_humidity_pct"),
        atmospheric_pressure_kpa: toFormValue(testConditions.atmospheric_pressure_kpa, testConditionsDashFields, "atmospheric_pressure_kpa"),

        road_ambient_temp_c: toFormValue(roadConditions.road_ambient_temperature_c, roadConditionsDashFields, "road_ambient_temperature_c"),
        road_ambient_humidity_pct: toFormValue(roadConditions.road_relative_humidity_pct, roadConditionsDashFields, "road_relative_humidity_pct"),

        electric_frequency_hz: toFormValue(powerSupply.frequency_hz, powerSupplyDashFields, "frequency_hz"),
        voltage_phase_a_zero: toFormValue(powerSupply.phase_a_n_voltage_v, powerSupplyDashFields, "phase_a_n_voltage_v"),
        voltage_phase_b_zero: toFormValue(powerSupply.phase_b_n_voltage_v, powerSupplyDashFields, "phase_b_n_voltage_v"),
        voltage_phase_c_zero: toFormValue(powerSupply.phase_c_n_voltage_v, powerSupplyDashFields, "phase_c_n_voltage_v"),
        voltage_phase_ab: toFormValue(powerSupply.phase_ab_voltage_v, powerSupplyDashFields, "phase_ab_voltage_v"),
        voltage_phase_bc: toFormValue(powerSupply.phase_bc_voltage_v, powerSupplyDashFields, "phase_bc_voltage_v"),
        voltage_phase_ac: toFormValue(powerSupply.phase_ac_voltage_v, powerSupplyDashFields, "phase_ac_voltage_v"),

        brand_name: toFormValue(protocol.brand_name, protocolDashFields, "brand_name"),
        commercial_name: toFormValue(protocol.commercial_name, protocolDashFields, "commercial_name"),
        vin: toFormValue(protocol.vin, protocolDashFields, "vin"),
        category: toFormValue(protocol.vehicle_category, protocolDashFields, "vehicle_category"),
        body_type: toFormValue(protocol.body_type, protocolDashFields, "body_type"),
        mileage_km: toFormValue(measurement.mileage_km, measurementDashFields, "mileage_km"),
        tire_marking_front: toFormValue(protocol.wheel_marking_front, protocolDashFields, "wheel_marking_front"),
        tire_marking_rear: toFormValue(protocol.wheel_marking_rear, protocolDashFields, "wheel_marking_rear"),
        tire_season: toFormValue(protocol.tire_season, protocolDashFields, "tire_season"),
        tire_spikes_present: booleanToSelect(protocol.has_spikes),
        manufacture_year: toFormValue(protocol.manufacture_year, protocolDashFields, "manufacture_year"),
        color: toFormValue(protocol.color, protocolDashFields, "color"),

        wheel_formula: toFormValue(measurement.wheel_formula, measurementDashFields, "wheel_formula"),
        mufflers_count: toFormValue(measurement.mufflers_count, measurementDashFields, "mufflers_count"),
        seats_count: toFormValue(measurement.seats_count, measurementDashFields, "seats_count"),
        side_steps_present: booleanToSelect(measurement.steps_present),

        engine_model: toFormValue(measurement.engine_model, measurementDashFields, "engine_model"),
        engine_power_kw: toFormValue(measurement.engine_power_kw, measurementDashFields, "engine_power_kw"),
        engine_layout: toFormValue(measurement.engine_layout, measurementDashFields, "engine_layout"),
        cylinder_layout: toFormValue(measurement.cylinder_layout, measurementDashFields, "cylinder_layout"),
        cylinders_count: toFormValue(measurement.cylinders_count, measurementDashFields, "cylinders_count"),
        fuel_type: toFormValue(measurement.fuel_type, measurementDashFields, "fuel_type"),
        turbo_present: booleanToSelect(measurement.turbo_present),

        steering_booster_type: toFormValue(measurement.steering_booster_type, measurementDashFields, "steering_booster_type"),
        steering_backlash_deg: toFormValue(measurement.steering_backlash_deg, measurementDashFields, "steering_backlash_deg"),
        transmission_type: toFormValue(measurement.transmission_type, measurementDashFields, "transmission_type"),

        service_brake_type: toFormValue(brake.service_brake_type, brakeDashFields, "service_brake_type"),
        parking_brake_type: toFormValue(brake.parking_brake_type, brakeDashFields, "parking_brake_type"),
        service_brake_control_force_axle1_n: toFormValue(brake.service_brake_control_force_axle1_n, brakeDashFields, "service_brake_control_force_axle1_n"),
        service_brake_control_force_axle2_n: toFormValue(brake.service_brake_control_force_axle2_n, brakeDashFields, "service_brake_control_force_axle2_n"),
        parking_brake_control_force_n: toFormValue(brake.parking_brake_control_force_n, brakeDashFields, "parking_brake_control_force_n"),
        axle_1_brake_difference_pct: toFormValue(brake.axle_1_brake_difference_pct, brakeDashFields, "axle_1_brake_difference_pct"),
        axle_2_brake_difference_pct: toFormValue(brake.axle_2_brake_difference_pct, brakeDashFields, "axle_2_brake_difference_pct"),
        service_brake_front_left_kn: toFormValue(brake.service_brake_front_left_kn, brakeDashFields, "service_brake_front_left_kn"),
        service_brake_front_right_kn: toFormValue(brake.service_brake_front_right_kn, brakeDashFields, "service_brake_front_right_kn"),
        service_brake_rear_left_kn: toFormValue(brake.service_brake_rear_left_kn, brakeDashFields, "service_brake_rear_left_kn"),
        service_brake_rear_right_kn: toFormValue(brake.service_brake_rear_right_kn, brakeDashFields, "service_brake_rear_right_kn"),
        parking_brake_left_kn: toFormValue(brake.parking_brake_left_kn, brakeDashFields, "parking_brake_left_kn"),
        parking_brake_right_kn: toFormValue(brake.parking_brake_right_kn, brakeDashFields, "parking_brake_right_kn"),

        low_beam_count: toFormValue(light.low_beam_count, lightDashFields, "low_beam_count"),
        low_beam_color: toFormValue(light.low_beam_color, lightDashFields, "low_beam_color"),
        high_beam_count: toFormValue(light.high_beam_count, lightDashFields, "high_beam_count"),
        high_beam_color: toFormValue(light.high_beam_color, lightDashFields, "high_beam_color"),
        front_fog_count: toFormValue(light.front_fog_count, lightDashFields, "front_fog_count"),
        front_fog_color: toFormValue(light.front_fog_color, lightDashFields, "front_fog_color"),
        reverse_light_count: toFormValue(light.reverse_light_count, lightDashFields, "reverse_light_count"),
        reverse_light_color: toFormValue(light.reverse_light_color, lightDashFields, "reverse_light_color"),
        turn_signal_count: toFormValue(light.turn_signal_count, lightDashFields, "turn_signal_count"),
        turn_signal_color: toFormValue(light.turn_signal_color, lightDashFields, "turn_signal_color"),
        front_position_light_count: toFormValue(light.front_position_light_count, lightDashFields, "front_position_light_count"),
        front_position_light_color: toFormValue(light.front_position_light_color, lightDashFields, "front_position_light_color"),
        rear_position_light_count: toFormValue(light.rear_position_light_count, lightDashFields, "rear_position_light_count"),
        rear_position_light_color: toFormValue(light.rear_position_light_color, lightDashFields, "rear_position_light_color"),
        main_brake_signal_count: toFormValue(light.main_brake_signal_count, lightDashFields, "main_brake_signal_count"),
        main_brake_signal_color: toFormValue(light.main_brake_signal_color, lightDashFields, "main_brake_signal_color"),
        additional_brake_signal_count: toFormValue(light.additional_brake_signal_count, lightDashFields, "additional_brake_signal_count"),
        additional_brake_signal_color: toFormValue(light.additional_brake_signal_color, lightDashFields, "additional_brake_signal_color"),
        rear_fog_count: toFormValue(light.rear_fog_count, lightDashFields, "rear_fog_count"),
        rear_fog_color: toFormValue(light.rear_fog_color, lightDashFields, "rear_fog_color"),
        plate_light_count: toFormValue(light.plate_light_count, lightDashFields, "plate_light_count"),
        plate_light_color: toFormValue(light.plate_light_color, lightDashFields, "plate_light_color"),
        daytime_running_light_count: toFormValue(light.daytime_running_light_count, lightDashFields, "daytime_running_light_count"),
        daytime_running_light_color: toFormValue(light.daytime_running_light_color, lightDashFields, "daytime_running_light_color"),

        parking_light_count: toFormValue(light.parking_light_count, lightDashFields, "parking_light_count"),
        parking_light_color: toFormValue(light.parking_light_color, lightDashFields, "parking_light_color"),
        rear_parking_light_count: toFormValue(light.rear_parking_light_count, lightDashFields, "rear_parking_light_count"),
        rear_parking_light_color: toFormValue(light.rear_parking_light_color, lightDashFields, "rear_parking_light_color"),
        adaptive_front_lighting_count: toFormValue(light.adaptive_front_lighting_count, lightDashFields, "adaptive_front_lighting_count"),
        adaptive_front_lighting_color: toFormValue(light.adaptive_front_lighting_color, lightDashFields, "adaptive_front_lighting_color"),

        headlight_type: toFormValue(light.headlight_type, lightDashFields, "headlight_type"),
        headlight_washer_present: booleanToSelect(light.headlight_washer_present),

        left_34v_cd: toFormValue(light.left_34v_cd, lightDashFields, "left_34v_cd"),
        left_52h_cd: toFormValue(light.left_52h_cd, lightDashFields, "left_52h_cd"),
        left_high_beam_cd: toFormValue(light.left_high_beam_cd, lightDashFields, "left_high_beam_cd"),
        right_34v_cd: toFormValue(light.right_34v_cd, lightDashFields, "right_34v_cd"),
        right_52h_cd: toFormValue(light.right_52h_cd, lightDashFields, "right_52h_cd"),
        right_high_beam_cd: toFormValue(light.right_high_beam_cd, lightDashFields, "right_high_beam_cd"),
        turn_signal_frequency_per_min: toFormValue(light.turn_signal_frequency_per_min, lightDashFields, "turn_signal_frequency_per_min"),
        turn_signal_frequency_hz: toFormValue(light.turn_signal_frequency_hz, lightDashFields, "turn_signal_frequency_hz"),

        low_beam_upper_point_mm: toFormValue(light.low_beam_upper_point_mm, lightDashFields, "low_beam_upper_point_mm"),
        low_beam_lower_point_mm: toFormValue(light.low_beam_lower_point_mm, lightDashFields, "low_beam_lower_point_mm"),
        fog_light_upper_point_mm: toFormValue(light.fog_light_upper_point_mm, lightDashFields, "fog_light_upper_point_mm"),
        fog_light_lower_point_mm: toFormValue(light.fog_light_lower_point_mm, lightDashFields, "fog_light_lower_point_mm"),
        fog_light_left_distance_mm: toFormValue(light.fog_light_left_distance_mm, lightDashFields, "fog_light_left_distance_mm"),
        fog_light_right_distance_mm: toFormValue(light.fog_light_right_distance_mm, lightDashFields, "fog_light_right_distance_mm"),
        brake_signal_upper_point_mm: toFormValue(light.brake_signal_upper_point_mm, lightDashFields, "brake_signal_upper_point_mm"),
        brake_signal_lower_point_mm: toFormValue(light.brake_signal_lower_point_mm, lightDashFields, "brake_signal_lower_point_mm"),
        brake_signal_left_distance_mm: toFormValue(light.brake_signal_left_distance_mm, lightDashFields, "brake_signal_left_distance_mm"),
        brake_signal_right_distance_mm: toFormValue(light.brake_signal_right_distance_mm, lightDashFields, "brake_signal_right_distance_mm"),
        additional_brake_signal_from_glass_edge_mm: toFormValue(light.additional_brake_signal_from_glass_edge_mm, lightDashFields, "additional_brake_signal_from_glass_edge_mm"),
        additional_brake_signal_from_support_surface_mm: toFormValue(light.additional_brake_signal_from_support_surface_mm, lightDashFields, "additional_brake_signal_from_support_surface_mm"),
        additional_brake_signal_optical_center_shift_mm: toFormValue(light.additional_brake_signal_optical_center_shift_mm, lightDashFields, "additional_brake_signal_optical_center_shift_mm"),
        rear_fog_upper_point_mm: toFormValue(light.rear_fog_upper_point_mm, lightDashFields, "rear_fog_upper_point_mm"),
        rear_fog_lower_point_mm: toFormValue(light.rear_fog_lower_point_mm, lightDashFields, "rear_fog_lower_point_mm"),

        spare_wheel_present: booleanToSelect(measurement.spare_wheel_present),
        steering_lock_present: booleanToSelect(measurement.steering_lock_present),
        gas_equipment_present: booleanToSelect(measurement.gas_equipment_present),
        glonass_button_present: booleanToSelect(measurement.glonass_button_present),

        tire_depth_fl_mm: toFormValue(measurement.tire_depth_fl_mm, measurementDashFields, "tire_depth_fl_mm"),
        tire_depth_rl_mm: toFormValue(measurement.tire_depth_rl_mm, measurementDashFields, "tire_depth_rl_mm"),
        tire_depth_fr_mm: toFormValue(measurement.tire_depth_fr_mm, measurementDashFields, "tire_depth_fr_mm"),
        tire_depth_rr_mm: toFormValue(measurement.tire_depth_rr_mm, measurementDashFields, "tire_depth_rr_mm"),
        bumper_ends_bent_to_body: booleanToSelect(measurement.bumper_bends_to_body),
        bumper_to_body_distance_mm: toFormValue(measurement.bumper_to_body_distance_mm, measurementDashFields, "bumper_to_body_distance_mm"),
        opening_roof_present: booleanToSelect(measurement.opening_roof_present),
        fuel_leak_prevention_measure: toFormValue(measurement.fuel_tank_leak_protection_measure, measurementDashFields, "fuel_tank_leak_protection_measure"),
        protruding_elements_doors_mm: toFormValue(measurement.protruding_elements_doors_mm, measurementDashFields, "protruding_elements_doors_mm"),
        protruding_elements_other_mm: toFormValue(measurement.protruding_elements_other_mm, measurementDashFields, "protruding_elements_other_mm"),
        glass_transparency_right_pct: toFormValue(measurement.glass_transparency_right_pct, measurementDashFields, "glass_transparency_right_pct"),
        glass_transparency_left_pct: toFormValue(measurement.glass_transparency_left_pct, measurementDashFields, "glass_transparency_left_pct"),
        glass_transparency_windshield_pct: toFormValue(measurement.glass_transparency_windshield_pct, measurementDashFields, "glass_transparency_windshield_pct"),
        sun_strip_width_mm: toFormValue(measurement.sun_strip_width_mm, measurementDashFields, "sun_strip_width_mm"),
        speed_by_speedometer_kmh: toFormValue(measurement.speed_by_speedometer_kmh, measurementDashFields, "speed_by_speedometer_kmh"),
        actual_speed_kmh: toFormValue(measurement.actual_speed_kmh, measurementDashFields, "actual_speed_kmh"),
        exhaust_noise_constant_db: toFormValue(measurement.exhaust_noise_constant_db, measurementDashFields, "exhaust_noise_constant_db"),
        exhaust_noise_deceleration_db: toFormValue(measurement.exhaust_noise_deceleration_db, measurementDashFields, "exhaust_noise_deceleration_db"),
        co_min_pct: toFormValue(measurement.co_min_pct, measurementDashFields, "co_min_pct"),
        co_max_pct: toFormValue(measurement.co_max_pct, measurementDashFields, "co_max_pct"),
        light_absorption_1: toFormValue(measurement.light_absorption_1, measurementDashFields, "light_absorption_1"),
        light_absorption_2: toFormValue(measurement.light_absorption_2, measurementDashFields, "light_absorption_2"),
        light_absorption_3: toFormValue(measurement.light_absorption_3, measurementDashFields, "light_absorption_3"),
        light_absorption_4: toFormValue(measurement.light_absorption_4, measurementDashFields, "light_absorption_4"),
        light_absorption_5: toFormValue(measurement.light_absorption_5, measurementDashFields, "light_absorption_5"),
        light_absorption_6: toFormValue(measurement.light_absorption_6, measurementDashFields, "light_absorption_6"),
        vehicle_length_mm: toFormValue(measurement.vehicle_length_mm, measurementDashFields, "vehicle_length_mm"),
        vehicle_width_mm: toFormValue(measurement.vehicle_width_mm, measurementDashFields, "vehicle_width_mm"),
        vehicle_height_mm: toFormValue(measurement.vehicle_height_mm, measurementDashFields, "vehicle_height_mm"),
        vehicle_weight_kg: toFormValue(measurement.vehicle_weight_kg, measurementDashFields, "vehicle_weight_kg"),
        axle1_load_kg: toFormValue(measurement.axle1_load_kg, measurementDashFields, "axle1_load_kg"),
        axle2_load_kg: toFormValue(measurement.axle2_load_kg, measurementDashFields, "axle2_load_kg"),
    };
}

function buildProtocolPayload(form) {
    const payload = {
        protocol_number: formatProtocolNumber(form.protocol_number),
        appendix_number: emptyToNull(form.appendix_number),
        protocol_date: emptyToNull(form.protocol_date),
        owner_last_name: emptyToNull(form.owner_last_name),
        owner_first_name: emptyToNull(form.owner_first_name),
        owner_middle_name: emptyToNull(form.owner_middle_name),
        manufacturer_info: emptyToNull(form.manufacturer_info),

        brand_name: emptyToNull(form.brand_name),
        commercial_name: emptyToNull(form.commercial_name),
        vin: emptyToNull(form.vin),
        vehicle_category: emptyToNull(form.category),
        body_type: emptyToNull(form.body_type),
        wheel_marking_front: emptyToNull(form.tire_marking_front),
        wheel_marking_rear: emptyToNull(form.tire_marking_rear),
        tire_season: emptyToNull(form.tire_season),
        has_spikes: stringToBooleanOrNull(form.tire_spikes_present),
        manufacture_year: emptyToNull(form.manufacture_year),
        color: emptyToNull(form.color),
        dash_fields: buildDashFields(form, PROTOCOL_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, PROTOCOL_NUMERIC_FIELDS);
}

function buildTestConditionsPayload(form) {
    const payload = {
        ambient_temperature_c: emptyToNull(form.ambient_temp_c),
        relative_humidity_pct: emptyToNull(form.ambient_humidity_pct),
        atmospheric_pressure_kpa: emptyToNull(form.atmospheric_pressure_kpa),
        dash_fields: buildDashFields(form, TEST_CONDITIONS_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, TEST_CONDITIONS_NUMERIC_FIELDS);
}

function buildRoadConditionsPayload(form) {
    const payload = {
        road_ambient_temperature_c: emptyToNull(form.road_ambient_temp_c),
        road_relative_humidity_pct: emptyToNull(form.road_ambient_humidity_pct),
        dash_fields: buildDashFields(form, ROAD_CONDITIONS_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, ROAD_CONDITIONS_NUMERIC_FIELDS);
}

function buildPowerSupplyPayload(form) {
    const payload = {
        frequency_hz: emptyToNull(form.electric_frequency_hz),
        phase_a_n_voltage_v: emptyToNull(form.voltage_phase_a_zero),
        phase_b_n_voltage_v: emptyToNull(form.voltage_phase_b_zero),
        phase_c_n_voltage_v: emptyToNull(form.voltage_phase_c_zero),
        phase_ab_voltage_v: emptyToNull(form.voltage_phase_ab),
        phase_bc_voltage_v: emptyToNull(form.voltage_phase_bc),
        phase_ac_voltage_v: emptyToNull(form.voltage_phase_ac),
        dash_fields: buildDashFields(form, POWER_SUPPLY_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, POWER_SUPPLY_NUMERIC_FIELDS);
}

function buildMeasurementPayload(form) {
    const payload = {
        mileage_km: emptyToNull(form.mileage_km),

        wheel_formula: emptyToNull(form.wheel_formula),
        mufflers_count: emptyToNull(form.mufflers_count),
        seats_count: emptyToNull(form.seats_count),
        steps_present: stringToBooleanOrNull(form.side_steps_present),

        engine_model: emptyToNull(form.engine_model),
        engine_power_kw: emptyToNull(form.engine_power_kw),
        engine_layout: emptyToNull(form.engine_layout),
        cylinder_layout: emptyToNull(form.cylinder_layout),
        cylinders_count: emptyToNull(form.cylinders_count),
        fuel_type: emptyToNull(form.fuel_type),
        turbo_present: stringToBooleanOrNull(form.turbo_present),

        steering_booster_type: emptyToNull(form.steering_booster_type),
        steering_backlash_deg: emptyToNull(form.steering_backlash_deg),
        transmission_type: emptyToNull(form.transmission_type),

        tire_depth_fl_mm: emptyToNull(form.tire_depth_fl_mm),
        tire_depth_fr_mm: emptyToNull(form.tire_depth_fr_mm),
        tire_depth_rl_mm: emptyToNull(form.tire_depth_rl_mm),
        tire_depth_rr_mm: emptyToNull(form.tire_depth_rr_mm),

        bumper_bends_to_body: stringToBooleanOrNull(form.bumper_ends_bent_to_body),
        bumper_to_body_distance_mm: emptyToNull(form.bumper_to_body_distance_mm),
        opening_roof_present: stringToBooleanOrNull(form.opening_roof_present),
        fuel_tank_leak_protection_measure: emptyToNull(form.fuel_leak_prevention_measure),

        protruding_elements_doors_mm: emptyToNull(form.protruding_elements_doors_mm),
        protruding_elements_other_mm: emptyToNull(form.protruding_elements_other_mm),

        glass_transparency_right_pct: emptyToNull(form.glass_transparency_right_pct),
        glass_transparency_left_pct: emptyToNull(form.glass_transparency_left_pct),
        glass_transparency_windshield_pct: emptyToNull(form.glass_transparency_windshield_pct),
        sun_strip_width_mm: emptyToNull(form.sun_strip_width_mm),

        speed_by_speedometer_kmh: emptyToNull(form.speed_by_speedometer_kmh),
        actual_speed_kmh: emptyToNull(form.actual_speed_kmh),

        exhaust_noise_constant_db: emptyToNull(form.exhaust_noise_constant_db),
        exhaust_noise_deceleration_db: emptyToNull(form.exhaust_noise_deceleration_db),
        co_min_pct: emptyToNull(form.co_min_pct),
        co_max_pct: emptyToNull(form.co_max_pct),

        light_absorption_1: emptyToNull(form.light_absorption_1),
        light_absorption_2: emptyToNull(form.light_absorption_2),
        light_absorption_3: emptyToNull(form.light_absorption_3),
        light_absorption_4: emptyToNull(form.light_absorption_4),
        light_absorption_5: emptyToNull(form.light_absorption_5),
        light_absorption_6: emptyToNull(form.light_absorption_6),

        vehicle_length_mm: emptyToNull(form.vehicle_length_mm),
        vehicle_width_mm: emptyToNull(form.vehicle_width_mm),
        vehicle_height_mm: emptyToNull(form.vehicle_height_mm),
        vehicle_weight_kg: emptyToNull(form.vehicle_weight_kg),

        axle1_load_kg: emptyToNull(form.axle1_load_kg),
        axle2_load_kg: emptyToNull(form.axle2_load_kg),

        spare_wheel_present: stringToBooleanOrNull(form.spare_wheel_present),
        steering_lock_present: stringToBooleanOrNull(form.steering_lock_present),
        gas_equipment_present: stringToBooleanOrNull(form.gas_equipment_present),
        glonass_button_present: stringToBooleanOrNull(form.glonass_button_present),

        dash_fields: buildDashFields(form, MEASUREMENT_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, MEASUREMENT_NUMERIC_FIELDS);
}

function buildBrakePayload(form) {
    const payload = {
        service_brake_type: emptyToNull(form.service_brake_type),
        parking_brake_type: emptyToNull(form.parking_brake_type),

        service_brake_control_force_axle1_n: emptyToNull(form.service_brake_control_force_axle1_n),
        service_brake_control_force_axle2_n: emptyToNull(form.service_brake_control_force_axle2_n),
        parking_brake_control_force_n: emptyToNull(form.parking_brake_control_force_n),

        axle_1_brake_difference_pct: emptyToNull(form.axle_1_brake_difference_pct),
        axle_2_brake_difference_pct: emptyToNull(form.axle_2_brake_difference_pct),

        service_brake_front_left_kn: emptyToNull(form.service_brake_front_left_kn),
        service_brake_front_right_kn: emptyToNull(form.service_brake_front_right_kn),
        service_brake_rear_left_kn: emptyToNull(form.service_brake_rear_left_kn),
        service_brake_rear_right_kn: emptyToNull(form.service_brake_rear_right_kn),

        parking_brake_left_kn: emptyToNull(form.parking_brake_left_kn),
        parking_brake_right_kn: emptyToNull(form.parking_brake_right_kn),

        dash_fields: buildDashFields(form, BRAKE_DASH_FIELDS),
    };
    return normalizeNumericPayload(payload, BRAKE_NUMERIC_FIELDS);
}

function buildLightPayload(form) {
    const payload = {
        low_beam_count: emptyToNull(form.low_beam_count),
        low_beam_color: emptyToNull(form.low_beam_color),

        high_beam_count: emptyToNull(form.high_beam_count),
        high_beam_color: emptyToNull(form.high_beam_color),

        front_fog_count: emptyToNull(form.front_fog_count),
        front_fog_color: emptyToNull(form.front_fog_color),

        reverse_light_count: emptyToNull(form.reverse_light_count),
        reverse_light_color: emptyToNull(form.reverse_light_color),

        turn_signal_count: emptyToNull(form.turn_signal_count),
        turn_signal_color: emptyToNull(form.turn_signal_color),

        front_position_light_count: emptyToNull(form.front_position_light_count),
        front_position_light_color: emptyToNull(form.front_position_light_color),

        rear_position_light_count: emptyToNull(form.rear_position_light_count),
        rear_position_light_color: emptyToNull(form.rear_position_light_color),

        main_brake_signal_count: emptyToNull(form.main_brake_signal_count),
        main_brake_signal_color: emptyToNull(form.main_brake_signal_color),

        additional_brake_signal_count: emptyToNull(form.additional_brake_signal_count),
        additional_brake_signal_color: emptyToNull(form.additional_brake_signal_color),

        rear_fog_count: emptyToNull(form.rear_fog_count),
        rear_fog_color: emptyToNull(form.rear_fog_color),

        plate_light_count: emptyToNull(form.plate_light_count),
        plate_light_color: emptyToNull(form.plate_light_color),

        daytime_running_light_count: emptyToNull(form.daytime_running_light_count),
        daytime_running_light_color: emptyToNull(form.daytime_running_light_color),

        parking_light_count: emptyToNull(form.parking_light_count),
        parking_light_color: emptyToNull(form.parking_light_color),

        rear_parking_light_count: emptyToNull(form.rear_parking_light_count),
        rear_parking_light_color: emptyToNull(form.rear_parking_light_color),

        adaptive_front_lighting_count: emptyToNull(form.adaptive_front_lighting_count),
        adaptive_front_lighting_color: emptyToNull(form.adaptive_front_lighting_color),

        headlight_type: emptyToNull(form.headlight_type),
        headlight_washer_present: stringToBooleanOrNull(form.headlight_washer_present),

        left_34v_cd: emptyToNull(form.left_34v_cd),
        left_52h_cd: emptyToNull(form.left_52h_cd),
        left_high_beam_cd: emptyToNull(form.left_high_beam_cd),

        right_34v_cd: emptyToNull(form.right_34v_cd),
        right_52h_cd: emptyToNull(form.right_52h_cd),
        right_high_beam_cd: emptyToNull(form.right_high_beam_cd),

        turn_signal_frequency_per_min: emptyToNull(form.turn_signal_frequency_per_min),
        turn_signal_frequency_hz: emptyToNull(form.turn_signal_frequency_hz),

        low_beam_upper_point_mm: emptyToNull(form.low_beam_upper_point_mm),
        low_beam_lower_point_mm: emptyToNull(form.low_beam_lower_point_mm),

        fog_light_upper_point_mm: emptyToNull(form.fog_light_upper_point_mm),
        fog_light_lower_point_mm: emptyToNull(form.fog_light_lower_point_mm),
        fog_light_left_distance_mm: emptyToNull(form.fog_light_left_distance_mm),
        fog_light_right_distance_mm: emptyToNull(form.fog_light_right_distance_mm),

        brake_signal_upper_point_mm: emptyToNull(form.brake_signal_upper_point_mm),
        brake_signal_lower_point_mm: emptyToNull(form.brake_signal_lower_point_mm),
        brake_signal_left_distance_mm: emptyToNull(form.brake_signal_left_distance_mm),
        brake_signal_right_distance_mm: emptyToNull(form.brake_signal_right_distance_mm),

        additional_brake_signal_from_glass_edge_mm: emptyToNull(form.additional_brake_signal_from_glass_edge_mm),
        additional_brake_signal_from_support_surface_mm: emptyToNull(form.additional_brake_signal_from_support_surface_mm),
        additional_brake_signal_optical_center_shift_mm: emptyToNull(form.additional_brake_signal_optical_center_shift_mm),

        rear_fog_upper_point_mm: emptyToNull(form.rear_fog_upper_point_mm),
        rear_fog_lower_point_mm: emptyToNull(form.rear_fog_lower_point_mm),

        dash_fields: buildDashFields(form, LIGHT_DASH_FIELDS),
    };

    return normalizeNumericPayload(payload, LIGHT_NUMERIC_FIELDS);
}

function ProtocolInspection() {
    const {id} = useParams();
    const navigate = useNavigate();

    const currentProtocolId = id;

    const [form, setForm] = useState(initialForm);
    const [photos, setPhotos] = useState([]);

    const formStatusRef = useRef("");
    const protocolLockActiveRef = useRef(false);
    const appendixManuallyEditedRef = useRef(false);

    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const [blockErrors, setBlockErrors] = useState({});

    const headerRef = useRef(null);
    const conditionsRef = useRef(null);
    const vehicleRef = useRef(null);
    const engineRef = useRef(null);
    const steeringTransmissionRef = useRef(null);
    const brakesRef = useRef(null);
    const lightsMainRef = useRef(null);
    const lightsGeometryRef = useRef(null);
    const miscRef = useRef(null);

    const scrollToBlock = (blockRef) => {
        setTimeout(() => {
            blockRef.current?.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }, 100);
    };

    const setBlockErrorAndScroll = (blockKey, blockRef, error) => {
        const errorText = formatApiError(error.response?.data);

        setBlockErrors((prev) => ({
            ...prev,
            [blockKey]: errorText,
        }));

        scrollToBlock(blockRef);
    };

    const getMeasurementErrorTarget = (error) => {
        const errorFields = getErrorFields(error.response?.data);

        if (hasAnyField(errorFields, MEASUREMENT_ENGINE_FIELDS)) {
            return {
                key: "engine",
                ref: engineRef,
            };
        }

        if (hasAnyField(errorFields, MEASUREMENT_STEERING_TRANSMISSION_FIELDS)) {
            return {
                key: "steeringTransmission",
                ref: steeringTransmissionRef,
            };
        }

        if (hasAnyField(errorFields, MEASUREMENT_MISC_FIELDS)) {
            return {
                key: "misc",
                ref: miscRef,
            };
        }

        return {
            key: "vehicle",
            ref: vehicleRef,
        };
    };

    const getLightErrorTarget = (error) => {
        const errorFields = getErrorFields(error.response?.data);

        if (hasAnyField(errorFields, LIGHT_GEOMETRY_FIELDS)) {
            return {
                key: "lightsGeometry",
                ref: lightsGeometryRef,
            };
        }

        return {
            key: "lightsMain",
            ref: lightsMainRef,
        };
    };

    const handleChange = (e) => {
        const {name, value} = e.target;

        if (name === "appendix_number") {
            appendixManuallyEditedRef.current = true;

            setForm((prev) => ({
                ...prev,
                appendix_number: value,
            }));

            return;
        }

        if (name === "protocol_number") {
            setForm((prev) => ({
                ...prev,
                protocol_number: value,
                appendix_number: appendixManuallyEditedRef.current
                    ? prev.appendix_number
                    : value,
            }));

            return;
        }

        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const releaseProtocolLock = async () => {
        if (!currentProtocolId) {
            return;
        }

        if (!protocolLockActiveRef.current) {
            return;
        }

        if (formStatusRef.current === "completed") {
            return;
        }

        try {
            protocolLockActiveRef.current = false;

            await api.post(`/cars/protocols/${currentProtocolId}/return-to-draft/`);

            formStatusRef.current = "draft";

            setForm((prev) => ({
                ...prev,
                status: "draft",
            }));
        } catch (error) {
            console.error("Ошибка освобождения протокола:", error);

            protocolLockActiveRef.current = true;

            throw error;
        }
    };

    const releaseProtocolLockOnUnload = () => {
        if (!currentProtocolId) {
            return;
        }

        if (!protocolLockActiveRef.current) {
            return;
        }

        if (formStatusRef.current === "completed") {
            return;
        }

        protocolLockActiveRef.current = false;

        const accessToken = localStorage.getItem("accessToken");
        const baseUrl = api.client.defaults.baseURL || "";

        try {
            fetch(`${baseUrl}/cars/protocols/${currentProtocolId}/return-to-draft/`, {
                method: "POST",
                keepalive: true,
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    ...(accessToken ? {Authorization: `Bearer ${accessToken}`} : {}),
                },
                body: JSON.stringify({}),
            });
        } catch (error) {
            console.error("Ошибка отправки keepalive-запроса при закрытии вкладки:", error);
        }
    };

    const loadProtocol = async (
        protocolId = currentProtocolId,
        options = {}
    ) => {
        const {startEditing = false} = options;

        if (!protocolId) return;

        try {
            setLoading(true);
            setErrorMessage("");

            let response = await api.get(`/cars/protocols/${protocolId}/full/`);
            let data = response.data;

            if (startEditing && data.status !== "completed") {
                await api.post(`/cars/protocols/${protocolId}/start-editing/`);

                protocolLockActiveRef.current = true;

                response = await api.get(`/cars/protocols/${protocolId}/full/`);
                data = response.data;
            }

            const mappedForm = mapProtocolToForm(data);

            if (!mappedForm.appendix_number && mappedForm.protocol_number) {
                mappedForm.appendix_number = mappedForm.protocol_number;
            }

            appendixManuallyEditedRef.current = Boolean(
                mappedForm.appendix_number &&
                mappedForm.protocol_number &&
                mappedForm.appendix_number !== mappedForm.protocol_number
            );

            setForm(mappedForm);
            setPhotos(data.photos || []);
        } catch (error) {
            console.error("Ошибка загрузки протокола:", error);

            if (error.response?.status === 423) {
                protocolLockActiveRef.current = false;
                setErrorMessage(
                    `Протокол уже редактируется пользователем: ${
                        error.response.data?.locked_by_username || "неизвестно"
                    }`
                );
            } else {
                setErrorMessage("Не удалось загрузить данные протокола");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (id) {
            loadProtocol(id, {startEditing: true});
        } else {
            setErrorMessage("Не передан ID протокола");
        }
    }, [id]);

    useEffect(() => {
        formStatusRef.current = form.status;
    }, [form.status]);

    useEffect(() => {
        return () => {
            if (!currentProtocolId) {
                return;
            }

            if (!protocolLockActiveRef.current) {
                return;
            }

            if (formStatusRef.current === "completed") {
                return;
            }

            releaseProtocolLock().catch((error) => {
                console.error("Ошибка освобождения протокола при переходе со страницы:", error);
            });
        };
    }, [currentProtocolId]);

    useEffect(() => {
        const handlePageHide = () => {
            releaseProtocolLockOnUnload();
        };

        const handleBeforeUnload = () => {
            releaseProtocolLockOnUnload();
        };

        window.addEventListener("pagehide", handlePageHide);
        window.addEventListener("beforeunload", handleBeforeUnload);

        return () => {
            window.removeEventListener("pagehide", handlePageHide);
            window.removeEventListener("beforeunload", handleBeforeUnload);
        };
    }, [currentProtocolId]);

    useEffect(() => {
        if (!currentProtocolId) {
            return;
        }

        const heartbeatIntervalId = setInterval(() => {
            if (!protocolLockActiveRef.current) {
                return;
            }

            if (formStatusRef.current === "completed") {
                return;
            }

            api.post(`/cars/protocols/${currentProtocolId}/heartbeat/`)
                .catch((error) => {
                    if (error.response?.status === 403) {
                        protocolLockActiveRef.current = false;
                        setErrorMessage(
                            "Редактирование остановлено: протокол занят другим пользователем."
                        );
                        return;
                    }

                    console.error("Ошибка heartbeat протокола:", error);
                });
        }, 30000);

        return () => {
            clearInterval(heartbeatIntervalId);
        };
    }, [currentProtocolId]);

    const handleSave = async (options = {}) => {
        const {showSuccessMessage = true} = options;

        try {
            setSaving(true);
            setSuccessMessage("");
            setErrorMessage("");
            setBlockErrors({});

            const protocolId = currentProtocolId;

            if (!protocolId) {
                setErrorMessage("Не передан ID протокола");
                return false;
            }

            const saveSteps = [
                {
                    key: "header",
                    ref: headerRef,
                    request: () =>
                        api.patch(
                            `/cars/protocols/${protocolId}/update/`,
                            buildProtocolPayload(form)
                        ),
                },
                {
                    key: "conditions",
                    ref: conditionsRef,
                    request: async () => {
                        await api.patch(
                            `/cars/protocols/${protocolId}/test-conditions/update/`,
                            buildTestConditionsPayload(form)
                        );

                        await api.patch(
                            `/cars/protocols/${protocolId}/road-conditions/update/`,
                            buildRoadConditionsPayload(form)
                        );

                        await api.patch(
                            `/cars/protocols/${protocolId}/power-supply/update/`,
                            buildPowerSupplyPayload(form)
                        );
                    },
                },
                {
                    key: "vehicle",
                    ref: vehicleRef,
                    getErrorTarget: getMeasurementErrorTarget,
                    request: () =>
                        api.patch(
                            `/cars/protocols/${protocolId}/measurement/update/`,
                            buildMeasurementPayload(form)
                        ),
                },
                {
                    key: "brakes",
                    ref: brakesRef,
                    request: () =>
                        api.patch(
                            `/cars/protocols/${protocolId}/brake/update/`,
                            buildBrakePayload(form)
                        ),
                },
                {
                    key: "lightsMain",
                    ref: lightsMainRef,
                    getErrorTarget: getLightErrorTarget,
                    request: () =>
                        api.patch(
                            `/cars/protocols/${protocolId}/light/update/`,
                            buildLightPayload(form)
                        ),
                },
            ];

            for (const step of saveSteps) {
                try {
                    await step.request();
                } catch (error) {
                    console.error(`Ошибка сохранения блока ${step.key}:`, error);

                    const target = step.getErrorTarget
                        ? step.getErrorTarget(error)
                        : {
                            key: step.key,
                            ref: step.ref,
                        };

                    setBlockErrorAndScroll(target.key, target.ref, error);
                    setErrorMessage("Ошибка при сохранении данных. Проверьте выделенный блок.");

                    return false;
                }
            }

            await loadProtocol(protocolId);

            if (showSuccessMessage) {
                setSuccessMessage("Протокол успешно сохранён");
            }

            return true;
        } catch (error) {
            console.error("Ошибка сохранения:", error);
            setErrorMessage("Ошибка при сохранении данных");
            return false;
        } finally {
            setSaving(false);
        }
    };

    const handleCompleteProtocol = async () => {
        if (!currentProtocolId) {
            setErrorMessage("Не передан ID протокола");
            return;
        }

        const confirmed = window.confirm(
            "Завершить протокол? После этого он исчезнет из списка протоколов в работе и появится в завершённых."
        );

        if (!confirmed) {
            return;
        }

        try {
            setSaving(true);
            setSuccessMessage("");
            setErrorMessage("");

            const protocolPayload = {
                ...buildProtocolPayload(form),
                status: "completed",
            };

            await api.patch(`/cars/protocols/${currentProtocolId}/update/`, protocolPayload);

            protocolLockActiveRef.current = false;
            formStatusRef.current = "completed";

            setForm((prev) => ({
                ...prev,
                status: "completed",
            }));

            setSuccessMessage("Протокол переведён в статус «Завершён»");

            navigate("/protocols/completed");
        } catch (error) {
            console.error("Ошибка завершения протокола:", error);
            setErrorMessage("Не удалось завершить протокол");
        } finally {
            setSaving(false);
        }
    };

    const handleReturnToDraft = async () => {
        if (!currentProtocolId) {
            setErrorMessage("Не передан ID протокола");
            return;
        }

        const confirmed = window.confirm(
            "Вернуть протокол в черновик? После этого он снова появится в списке протоколов в работе."
        );

        if (!confirmed) {
            return;
        }

        try {
            setSaving(true);
            setSuccessMessage("");
            setErrorMessage("");

            await api.post(`/cars/protocols/${currentProtocolId}/return-to-draft/`);

            protocolLockActiveRef.current = false;
            formStatusRef.current = "draft";

            await loadProtocol(currentProtocolId);

            setSuccessMessage("Протокол возвращён в черновик");
        } catch (error) {
            console.error("Ошибка возврата протокола в черновик:", error);
            setErrorMessage("Не удалось вернуть протокол в черновик");
        } finally {
            setSaving(false);
        }
    };

    const handleGenerateDocx = async () => {
        if (!currentProtocolId) {
            setErrorMessage("Сначала сохраните протокол");
            return;
        }

        const saved = await handleSave({
            showSuccessMessage: false,
        });

        if (!saved) {
            return;
        }

        try {
            setErrorMessage("");
            setSuccessMessage("Данные сохранены, формируется DOCX...");

            const response = await api.generateProtocolDocx(currentProtocolId);

            const blob = new Blob([response.data], {
                type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            });

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = `protocol_${currentProtocolId}.docx`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            setSuccessMessage("DOCX успешно сформирован");
        } catch (error) {
            console.error("Ошибка генерации DOCX:", error);
            setErrorMessage("Не удалось сформировать DOCX");
        }
    };

    const commonSectionProps = {
        form,
        handleChange,
        textFieldSx,
        selectFieldSx,
        sectionPaperSx,
        sectionTitleSx,
        subsectionTitleSx,
    };

    const isCompleted = form.status === "completed";
    const actionButtons = (
        <Box
            sx={{
                display: "flex",
                gap: 1.5,
                flexWrap: "wrap",
                justifyContent: {
                    xs: "flex-start",
                    md: "flex-end",
                },
            }}
        >
            <Button
                variant="outlined"
                onClick={handleGenerateDocx}
                disabled={!currentProtocolId || saving || loading}
                sx={{
                    borderColor: "black",
                    color: "black",
                    borderRadius: 0,
                    textTransform: "none",
                    px: 3,
                    py: 1,
                    fontWeight: 800,
                    "&:hover": {
                        borderColor: "black",
                        bgcolor: "#eeeeee",
                    },
                }}
            >
                {saving ? "Сохранение..." : "Сформировать DOCX"}
            </Button>

            {isCompleted ? (
                <Button
                    variant="contained"
                    onClick={handleReturnToDraft}
                    disabled={saving || loading || !currentProtocolId}
                    sx={{
                        bgcolor: "white",
                        color: "black",
                        border: "2px solid black",
                        borderRadius: 0,
                        textTransform: "none",
                        px: 3,
                        py: 1,
                        fontWeight: 800,
                        boxShadow: "none",
                        "&:hover": {
                            bgcolor: "#eeeeee",
                            boxShadow: "none",
                        },
                    }}
                >
                    Вернуть в черновик
                </Button>
            ) : (
                <Button
                    variant="contained"
                    onClick={handleCompleteProtocol}
                    disabled={saving || loading || !currentProtocolId}
                    sx={{
                        bgcolor: "#333333",
                        color: "white",
                        borderRadius: 0,
                        textTransform: "none",
                        px: 3,
                        py: 1,
                        fontWeight: 800,
                        boxShadow: "none",
                        "&:hover": {
                            bgcolor: "#111111",
                            boxShadow: "none",
                        },
                    }}
                >
                    Завершить протокол
                </Button>
            )}

            <Button
                variant="contained"
                onClick={handleSave}
                disabled={saving || loading}
                sx={{
                    bgcolor: "black",
                    color: "white",
                    borderRadius: 0,
                    textTransform: "none",
                    px: 3,
                    py: 1,
                    fontWeight: 800,
                    boxShadow: "none",
                    "&:hover": {
                        bgcolor: "#222",
                        boxShadow: "none",
                    },
                }}
            >
                {saving ? "Сохранение..." : "Сохранить"}
            </Button>
        </Box>
    );

    return (
        <>
            <AppHeader beforeNavigate={releaseProtocolLock}/>

            <Box sx={pageSx}>
                <Box sx={pageInnerSx}>
                    <Box
                        sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "flex-start",
                            gap: 2,
                            flexWrap: "wrap",
                            mb: 3,
                        }}
                    >
                        <Box>
                            <Typography
                                variant="h4"
                                sx={{
                                    color: "black",
                                    fontWeight: 800,
                                    mb: 0.8,
                                }}
                            >
                                Осмотр автомобиля
                            </Typography>

                            <Typography
                                variant="body1"
                                sx={{
                                    color: "text.secondary",
                                    mb: 1.5,
                                }}
                            >
                                Заполнение данных осмотра, условий испытаний, фотографий и результатов замеров.
                            </Typography>

                            <Box
                                sx={{
                                    display: "flex",
                                    gap: 1,
                                    flexWrap: "wrap",
                                }}
                            >
                                <Chip
                                    label={`Протокол № ${form.protocol_number || currentProtocolId || "новый"}`}
                                    sx={{
                                        borderRadius: 0,
                                        bgcolor: "black",
                                        color: "white",
                                        fontWeight: 800,
                                    }}
                                />

                                <Chip
                                    label={
                                        form.brand_name || form.commercial_name
                                            ? `${form.brand_name || ""} ${form.commercial_name || ""}`.trim()
                                            : "Автомобиль не указан"
                                    }
                                    sx={{
                                        borderRadius: 0,
                                        bgcolor: "white",
                                        border: "1px solid black",
                                        color: "black",
                                        fontWeight: 800,
                                    }}
                                />

                                <Chip
                                    label={`Дата: ${formatDateForChip(form.protocol_date)}`}
                                    sx={{
                                        borderRadius: 0,
                                        bgcolor: "white",
                                        border: "1px solid black",
                                        color: "black",
                                        fontWeight: 800,
                                    }}
                                />
                            </Box>
                        </Box>

                        {actionButtons}
                    </Box>

                    {loading && (
                        <Alert
                            severity="info"
                            sx={{
                                mb: 2,
                                borderRadius: 0,
                            }}
                        >
                            Загрузка данных...
                        </Alert>
                    )}

                    {successMessage && (
                        <Alert
                            severity="success"
                            sx={{
                                mb: 2,
                                borderRadius: 0,
                            }}
                        >
                            {successMessage}
                        </Alert>
                    )}

                    {errorMessage && (
                        <Alert
                            severity="error"
                            sx={{
                                mb: 2,
                                borderRadius: 0,
                            }}
                        >
                            {errorMessage}
                        </Alert>
                    )}

                    <Box ref={headerRef}>
                        <BlockError message={blockErrors.header}/>
                        <ProtocolInspectionHeader {...commonSectionProps} />
                    </Box>

                    <Box ref={conditionsRef}>
                        <BlockError message={blockErrors.conditions}/>
                        <ProtocolInspectionConditions {...commonSectionProps} />
                    </Box>

                    <ProtocolInspectionPhotos
                        {...commonSectionProps}
                        protocolId={currentProtocolId}
                        photos={photos}
                        setPhotos={setPhotos}
                    />

                    <Box ref={vehicleRef}>
                        <BlockError message={blockErrors.vehicle}/>
                        <ProtocolInspectionVehicle {...commonSectionProps} />
                    </Box>

                    <Box ref={engineRef}>
                        <BlockError message={blockErrors.engine}/>
                        <ProtocolInspectionEngine {...commonSectionProps} />
                    </Box>

                    <Box ref={steeringTransmissionRef}>
                        <BlockError message={blockErrors.steeringTransmission}/>
                        <ProtocolInspectionSteeringTransmission {...commonSectionProps} />
                    </Box>

                    <Box ref={brakesRef}>
                        <BlockError message={blockErrors.brakes}/>
                        <ProtocolInspectionBrakes {...commonSectionProps} />
                    </Box>

                    <Box ref={lightsMainRef}>
                        <BlockError message={blockErrors.lightsMain}/>
                        <ProtocolInspectionLightsMain {...commonSectionProps} />
                    </Box>

                    <Box ref={lightsGeometryRef}>
                        <BlockError message={blockErrors.lightsGeometry}/>
                        <ProtocolInspectionLightsGeometry {...commonSectionProps} />
                    </Box>

                    <Box ref={miscRef}>
                        <BlockError message={blockErrors.misc}/>
                        <ProtocolInspectionMisc {...commonSectionProps} />
                    </Box>

                    <Box
                        sx={{
                            position: "sticky",
                            bottom: 0,
                            display: "flex",
                            justifyContent: "flex-end",
                            mt: 2,
                            py: 2,
                            bgcolor: "#f2f2f2",
                            borderTop: "2px solid black",
                            zIndex: 10,
                        }}
                    >
                        {actionButtons}
                    </Box>
                </Box>
            </Box>
        </>
    );
}

export default ProtocolInspection;