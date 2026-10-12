# V5 DOCX Placeholder Migration Inventory

## Scope

Source audited: `cars/templates/protocol_template_v5_source.docx`.

The template contains 253 unique placeholders. All 253 resolve in the generated context for the sampled protocol. This is an inventory and naming proposal only: the DOCX and runtime context keys have not been renamed.

## Proposed Canonical Contract

- Row condition: `a_<clause>_is_applicable` (boolean for `{%tr if %}`).
- Status cell: `a_<clause>_status` (for example, `соответствует` or the applicable non-applicability reason).
- Conclusion cell: `a_<clause>_conclusion` (normative/result text or `-`).
- Measurement: `a_<clause>_<measure>_value`.
- Measurement uncertainty: `a_<clause>_<measure>_uncertainty`.
- Shared protocol/vehicle identity fields are not clause results; migrate them under a shared namespace such as `protocol_*` or `vehicle_*`.

Legacy mappings:
- `applicable_<clause>` -> `a_<clause>_status`.
- `result_a_<clause>_conclusion` and `full_result_a_<clause>` -> `a_<clause>_conclusion`.
- Existing custom pairs such as `front_fog_a_8_10_1_status/conclusion` and `rear_fog_a_8_13_1_status/conclusion` should be normalized to the same clause-based names.
- Existing domain conditions such as `front_fog_present` and `winter_tires_present` should receive clause-based condition aliases during migration.

## Current Row Conditions

The v5 template uses these row-level conditions:

```text
{%tr if parking_light_present %}
{%tr if not parking_light_present %}
{%tr if front_fog_present %}
{%tr if not front_fog_present %}
{%tr if rear_parking_light_present %}
{%tr if not rear_parking_light_present %}
{%tr if rear_fog_present %}
{%tr if not rear_fog_present %}
{%tr if daytime_running_light_present %}
{%tr if not daytime_running_light_present %}
{%tr if adaptive_front_lighting_present %}
{%tr if not adaptive_front_lighting_present %}
{%tr if winter_tires_present %}
{%tr if a_21_7_numeric %}
{%tr if a_21_8_numeric %}
{%tr if a_23_1_electric %}
{%tr else %}
{%tr endif %}
```

No `{%tr elif %}` tags were found. Repeated copies of a tag in merged cells are the same row-level condition, not separate branches.

## Current Placeholder Inventory

### Applicability/status family (97)

```text
applicable_10_4, applicable_10_5, applicable_10_6, applicable_10_7_3, applicable_10_9_1, applicable_10_9_2, applicable_10_9_2_1, applicable_10_9_2_2, applicable_10_9_2_3, applicable_10_9_2_4, applicable_10_9_2_5, applicable_10_9_3, applicable_11_16, applicable_13_14, applicable_13_6, applicable_16_11, applicable_16_12, applicable_16_13, applicable_16_14, applicable_16_15, applicable_16_16, applicable_16_17, applicable_16_2, applicable_17_2, applicable_17_3, applicable_18_3, applicable_18_4_2, applicable_18_4_4, applicable_18_5, applicable_1_2_1, applicable_1_2_2, applicable_1_2_3, applicable_20_1, applicable_20_2, applicable_20_3, applicable_20_5, applicable_20_5_1, applicable_20_5_2, applicable_20_5_3, applicable_20_6, applicable_20_7, applicable_20_8, applicable_21_3, applicable_21_4, applicable_21_5, applicable_21_6, applicable_21_7, applicable_21_8, applicable_22_3, applicable_22_4, applicable_22_5_1, applicable_22_5_2, applicable_22_5_3, applicable_22_5_4, applicable_22_5_5, applicable_22_5_6_1, applicable_22_5_6_2, applicable_22_5_6_3, applicable_23_1, applicable_23_2, applicable_24_6, applicable_26_12, applicable_26_7, applicable_26_8, applicable_2_1, applicable_3_1, applicable_3_2, applicable_5, applicable_5_11_1, applicable_5_11_6, applicable_5_11_8, applicable_5_16, applicable_5_1_2_2, applicable_5_1_4_2_1, applicable_5_5_1_3, applicable_6_4, applicable_6_5, applicable_7_3, applicable_7_5, applicable_7_6, applicable_8_1, applicable_8_13_1, applicable_8_13_2, applicable_8_18_1, applicable_8_18_2, applicable_8_18_3, applicable_8_18_4, applicable_8_19, applicable_8_20_3, applicable_8_20_8, applicable_8_24_1, applicable_8_24_2, applicable_8_24_3, applicable_8_25, applicable_8_27, applicable_8_7, applicable_stb_914_e_4_7
```

### Result/conclusion family (22)

```text
full_result_a_10_7_2, full_result_a_11_8_sun_strip, full_result_a_21_9, result_a_10_5_conclusion, result_a_10_6_conclusion, result_a_16_17_conclusion, result_a_18_5_conclusion, result_a_23_2_conclusion, result_a_24_6_conclusion, result_a_26_12_conclusion, result_a_26_7_conclusion, result_a_3_2_conclusion, result_a_6_5_conclusion, result_a_8_13_1_conclusion, result_a_8_20_3_conclusion, result_a_8_20_8_conclusion, result_a_8_24_1_conclusion, result_a_8_24_2_conclusion, result_a_8_24_3_conclusion, result_a_8_25_conclusion, result_a_8_27_conclusion, result_a_8_7_conclusion
```

Additional custom split pairs:

```text
front_fog_a_8_10_1_status, front_fog_a_8_10_1_conclusion
front_fog_a_8_10_2_status, front_fog_a_8_10_2_conclusion
front_fog_a_8_10_3_status, front_fog_a_8_10_3_conclusion
rear_fog_a_8_13_1_status, rear_fog_a_8_13_1_conclusion
rear_fog_a_8_13_2_status, rear_fog_a_8_13_2_conclusion
```

### Measurement and calculated values (61)

```text
additional_brake_signal_count_value, additional_brake_signal_from_glass_edge_mm, additional_brake_signal_from_support_surface_mm, additional_brake_signal_optical_center_shift_mm, brake_signal_left_distance_mm, brake_signal_lower_point_mm, brake_signal_right_distance_mm, brake_signal_upper_point_mm, co_max_21_7_with_unit, co_min_21_7_with_unit, fog_light_left_distance_8_10_1, fog_light_lower_point_8_10_2, fog_light_right_distance_8_10_1, fog_light_upper_point_8_10_2, light_absorption_avg_21_8_with_unit, tire_depth_fl_10_7_2, tire_depth_fl_10_7_3, tire_depth_fr_10_7_2, tire_depth_fr_10_7_3, tire_depth_rl_10_7_2, tire_depth_rl_10_7_3, tire_depth_rr_10_7_2, tire_depth_rr_10_7_3, u_actual_speed_kmh, u_additional_brake_signal_from_glass_edge_mm, u_additional_brake_signal_from_support_surface_mm, u_additional_brake_signal_optical_center_shift_mm, u_axle_1_brake_difference_pct, u_axle_2_brake_difference_pct, u_brake_signal_left_distance_mm, u_brake_signal_lower_point_mm, u_brake_signal_right_distance_mm, u_brake_signal_upper_point_mm, u_bumper_to_body_distance_mm, u_calc_total_high_beam_cd, u_glass_transparency_left_pct, u_glass_transparency_right_pct, u_glass_transparency_windshield_pct, u_left_34v_cd, u_left_52h_cd, u_low_beam_lower_point_mm, u_low_beam_upper_point_mm, u_parking_brake_control_force_n, u_parking_brake_specific_force, u_protruding_elements_doors_mm, u_protruding_elements_other_mm, u_right_34v_cd, u_right_52h_cd, u_service_brake_control_force_axle1_n, u_service_brake_control_force_axle2_n, u_service_brake_specific_force, u_steering_backlash_deg, u_turn_signal_frequency_hz, u_turn_signal_frequency_per_min, u_vehicle_height_mm, u_vehicle_length_mm, u_vehicle_width_mm, vehicle_height_mm, vehicle_length_mm, vehicle_width_mm
```

### Other/shared values (73)

```text
actual_speed_kmh, ambient_temperature_c, atmospheric_pressure_kpa, axle_1_brake_difference_pct, axle_2_brake_difference_pct, body_type, brand_name, bumper_to_body_distance_mm, calc_parking_brake_specific_force, calc_service_brake_specific_force, calc_total_high_beam_cd, commercial_name, exhaust_noise_constant_db, exhaust_noise_deceleration_db, glass_transparency_left_pct, glass_transparency_right_pct, glass_transparency_windshield_pct, high_beam_count_value, left_34v_cd, left_52h_cd, left_high_beam_cd, light_device_conclusion, low_beam_lower_point_mm, low_beam_upper_point_mm, manufacturer_info, mileage_21_9, owner_first_name, owner_last_name, owner_middle_name, parking_brake_control_force_n, phase_a_n_voltage_v, phase_ab_voltage_v, phase_ac_voltage_v, phase_b_n_voltage_v, phase_bc_voltage_v, phase_c_n_voltage_v, photo_gas_test, photo_noise_test, photo_stand_test, plate_light_count_value, protocol_date, protocol_number, protruding_elements_doors_mm, protruding_elements_other_mm, rear_fog_count_value, rear_fog_lower_point_8_13_2, rear_fog_upper_point_8_13_2, registration_number, relative_humidity_pct, reverse_light_count_value, right_34v_cd, right_52h_cd, right_high_beam_cd, road_ambient_temperature_c, road_relative_humidity_pct, service_brake_control_force_axle1_n, service_brake_control_force_axle2_n, speed_by_speedometer_kmh, steering_backlash_deg, sun_strip_width_11_8, turn_signal_frequency_hz, turn_signal_frequency_per_min, vin
```

## Migration Sequence

1. Add canonical aliases to context without removing current keys.
2. Migrate v5 and test rendered output and condition branches.
3. Migrate the old template.
4. Remove legacy aliases only after verifying both templates.
