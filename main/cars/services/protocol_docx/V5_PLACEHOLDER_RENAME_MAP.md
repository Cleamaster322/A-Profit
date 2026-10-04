# V5 Placeholder Rename Map

This file maps every unique `{{ ... }}` placeholder currently found in `protocol_template_v5_source.docx` to the proposed canonical name. It also lists the row-condition variable aliases. No template or runtime key has been renamed yet.

The inventory contains 253 unique interpolation placeholders; the sampled protocol context resolves all 253. When multiple old placeholders map to one canonical name, keep one output placeholder in the migrated template.

## Status placeholders

```text
{{ applicable_1_2_1 }} -> {{ a_1_2_1_status }}
{{ applicable_10_7_3 }} -> {{ a_10_7_3_conclusion }}
{{ applicable_1_2_3 }} -> {{ a_1_2_3_status }}
{{ applicable_1_2_2 }} -> {{ a_1_2_2_status }}
{{ applicable_2_1 }} -> {{ a_2_1_status }}
{{ applicable_21_7 }} -> {{ a_21_7_conclusion }}
{{ applicable_3_1 }} -> {{ a_3_1_status }}
{{ applicable_3_2 }} -> {{ a_3_2_status }}
{{ applicable_21_8 }} -> {{ a_21_8_conclusion }}
{{ applicable_5_1_2_2 }} -> {{ a_5_1_2_2_status }}
{{ applicable_5 }} -> {{ a_5_status }}
{{ applicable_5_5_1_3 }} -> {{ a_5_5_1_3_status }}
{{ applicable_23_1 }} -> {{ a_23_1_conclusion }}
{{ applicable_5_11_6 }} -> {{ a_5_11_6_status }}
{{ applicable_5_11_8 }} -> {{ a_5_11_8_status }}
{{ applicable_5_1_4_2_1 }} -> {{ a_5_1_4_2_1_status }}
{{ applicable_6_4 }} -> {{ a_6_4_status }}
{{ applicable_6_5 }} -> {{ a_6_5_status }}
{{ applicable_8_13_2 }} -> {{ a_8_13_2_conclusion }}
{{ applicable_7_5 }} -> {{ a_7_5_status }}
{{ applicable_7_6 }} -> {{ a_7_6_status }}
{{ applicable_8_1 }} -> {{ a_8_1_status }}
{{ applicable_5_11_1 }} -> {{ a_5_11_1_status }}
{{ applicable_5_16 }} -> {{ a_5_16_status }}
{{ applicable_7_3 }} -> {{ a_7_3_status }}
{{ applicable_8_7 }} -> {{ a_8_7_status }}
{{ applicable_8_13_1 }} -> {{ a_8_13_1_status }}
{{ applicable_8_18_1 }} -> {{ a_8_18_1_status }}
{{ applicable_8_18_2 }} -> {{ a_8_18_2_status }}
{{ applicable_8_18_3 }} -> {{ a_8_18_3_status }}
{{ applicable_8_18_4 }} -> {{ a_8_18_4_status }}
{{ applicable_8_19 }} -> {{ a_8_19_status }}
{{ applicable_8_20_3 }} -> {{ a_8_20_3_status }}
{{ applicable_8_20_8 }} -> {{ a_8_20_8_status }}
{{ applicable_8_24_1 }} -> {{ a_8_24_1_status }}
{{ applicable_8_24_2 }} -> {{ a_8_24_2_status }}
{{ applicable_8_24_3 }} -> {{ a_8_24_3_status }}
{{ applicable_8_25 }} -> {{ a_8_25_status }}
{{ applicable_8_27 }} -> {{ a_8_27_status }}
{{ applicable_10_4 }} -> {{ a_10_4_status }}
{{ applicable_10_5 }} -> {{ a_10_5_status }}
{{ applicable_10_6 }} -> {{ a_10_6_status }}
{{ applicable_10_9_1 }} -> {{ a_10_9_1_status }}
{{ applicable_10_9_2 }} -> {{ a_10_9_2_status }}
{{ applicable_10_9_2_1 }} -> {{ a_10_9_2_1_status }}
{{ applicable_10_9_2_2 }} -> {{ a_10_9_2_2_status }}
{{ applicable_10_9_2_3 }} -> {{ a_10_9_2_3_status }}
{{ applicable_10_9_2_4 }} -> {{ a_10_9_2_4_status }}
{{ applicable_10_9_2_5 }} -> {{ a_10_9_2_5_status }}
{{ applicable_10_9_3 }} -> {{ a_10_9_3_status }}
{{ applicable_11_16 }} -> {{ a_11_16_status }}
{{ applicable_13_6 }} -> {{ a_13_6_status }}
{{ applicable_13_14 }} -> {{ a_13_14_status }}
{{ applicable_16_2 }} -> {{ a_16_2_status }}
{{ applicable_16_11 }} -> {{ a_16_11_status }}
{{ applicable_16_12 }} -> {{ a_16_12_status }}
{{ applicable_16_13 }} -> {{ a_16_13_status }}
{{ applicable_16_14 }} -> {{ a_16_14_status }}
{{ applicable_16_15 }} -> {{ a_16_15_status }}
{{ applicable_16_16 }} -> {{ a_16_16_status }}
{{ applicable_16_17 }} -> {{ a_16_17_status }}
{{ applicable_17_2 }} -> {{ a_17_2_status }}
{{ applicable_17_3 }} -> {{ a_17_3_status }}
{{ applicable_18_3 }} -> {{ a_18_3_status }}
{{ applicable_18_4_2 }} -> {{ a_18_4_2_status }}
{{ applicable_18_4_4 }} -> {{ a_18_4_4_status }}
{{ applicable_18_5 }} -> {{ a_18_5_status }}
{{ applicable_20_1 }} -> {{ a_20_1_status }}
{{ applicable_20_2 }} -> {{ a_20_2_status }}
{{ applicable_20_3 }} -> {{ a_20_3_status }}
{{ applicable_20_5 }} -> {{ a_20_5_status }}
{{ applicable_20_5_1 }} -> {{ a_20_5_1_status }}
{{ applicable_20_5_2 }} -> {{ a_20_5_2_status }}
{{ applicable_20_5_3 }} -> {{ a_20_5_3_status }}
{{ applicable_20_6 }} -> {{ a_20_6_status }}
{{ applicable_20_7 }} -> {{ a_20_7_status }}
{{ applicable_20_8 }} -> {{ a_20_8_status }}
{{ applicable_21_3 }} -> {{ a_21_3_status }}
{{ applicable_21_4 }} -> {{ a_21_4_status }}
{{ applicable_21_5 }} -> {{ a_21_5_status }}
{{ applicable_21_6 }} -> {{ a_21_6_status }}
{{ applicable_22_3 }} -> {{ a_22_3_status }}
{{ applicable_22_4 }} -> {{ a_22_4_status }}
{{ applicable_22_5_1 }} -> {{ a_22_5_1_status }}
{{ applicable_22_5_2 }} -> {{ a_22_5_2_status }}
{{ applicable_22_5_3 }} -> {{ a_22_5_3_status }}
{{ applicable_22_5_4 }} -> {{ a_22_5_4_status }}
{{ applicable_22_5_5 }} -> {{ a_22_5_5_status }}
{{ applicable_22_5_6_1 }} -> {{ a_22_5_6_1_status }}
{{ applicable_22_5_6_2 }} -> {{ a_22_5_6_2_status }}
{{ applicable_22_5_6_3 }} -> {{ a_22_5_6_3_status }}
{{ applicable_23_2 }} -> {{ a_23_2_status }}
{{ applicable_24_6 }} -> {{ a_24_6_status }}
{{ applicable_26_7 }} -> {{ a_26_7_status }}
{{ applicable_26_8 }} -> {{ a_26_8_status }}
{{ applicable_26_12 }} -> {{ a_26_12_status }}
{{ applicable_stb_914_e_4_7 }} -> {{ a_stb_914_e_4_7_status }}
```

## Conclusion placeholders

```text
{{ result_a_3_2_conclusion }} -> {{ a_3_2_conclusion }}
{{ result_a_6_5_conclusion }} -> {{ a_6_5_conclusion }}
{{ result_a_8_7_conclusion }} -> {{ a_8_7_conclusion }}
{{ result_a_8_13_1_conclusion }} -> {{ a_8_13_1_conclusion }}
{{ result_a_8_20_3_conclusion }} -> {{ a_8_20_3_conclusion }}
{{ result_a_8_20_8_conclusion }} -> {{ a_8_20_8_conclusion }}
{{ result_a_8_24_1_conclusion }} -> {{ a_8_24_1_conclusion }}
{{ result_a_8_24_2_conclusion }} -> {{ a_8_24_2_conclusion }}
{{ result_a_8_24_3_conclusion }} -> {{ a_8_24_3_conclusion }}
{{ result_a_8_25_conclusion }} -> {{ a_8_25_conclusion }}
{{ result_a_8_27_conclusion }} -> {{ a_8_27_conclusion }}
{{ result_a_10_5_conclusion }} -> {{ a_10_5_conclusion }}
{{ result_a_10_6_conclusion }} -> {{ a_10_6_conclusion }}
{{ result_a_16_17_conclusion }} -> {{ a_16_17_conclusion }}
{{ result_a_18_5_conclusion }} -> {{ a_18_5_conclusion }}
{{ result_a_23_2_conclusion }} -> {{ a_23_2_conclusion }}
{{ result_a_24_6_conclusion }} -> {{ a_24_6_conclusion }}
{{ result_a_26_7_conclusion }} -> {{ a_26_7_conclusion }}
{{ result_a_26_12_conclusion }} -> {{ a_26_12_conclusion }}
{{ full_result_a_10_7_2 }} -> {{ a_10_7_2_conclusion }}
{{ full_result_a_11_8_sun_strip }} -> {{ a_11_8_conclusion }}
{{ full_result_a_21_9 }} -> {{ a_21_9_conclusion }}
{{ front_fog_a_8_10_1_status }} -> {{ a_8_10_1_status }}
{{ front_fog_a_8_10_1_conclusion }} -> {{ a_8_10_1_conclusion }}
{{ front_fog_a_8_10_2_status }} -> {{ a_8_10_2_status }}
{{ front_fog_a_8_10_2_conclusion }} -> {{ a_8_10_2_conclusion }}
{{ front_fog_a_8_10_3_status }} -> {{ a_8_10_3_status }}
{{ front_fog_a_8_10_3_conclusion }} -> {{ a_8_10_3_conclusion }}
{{ rear_fog_a_8_13_1_status }} -> {{ a_8_13_1_status }}
{{ rear_fog_a_8_13_1_conclusion }} -> {{ a_8_13_1_conclusion }}
{{ rear_fog_a_8_13_2_status }} -> {{ a_8_13_2_status }}
{{ rear_fog_a_8_13_2_conclusion }} -> {{ a_8_13_2_conclusion }}
```

## Condition placeholders

```text
{%tr if parking_light_present %} -> {%tr if a_8_25_parking_lights_present %}
{%tr if not parking_light_present %} -> {%tr if not a_8_25_parking_lights_present %}
{%tr if front_fog_present %} -> {%tr if a_8_10_is_applicable %}
{%tr if not front_fog_present %} -> {%tr if not a_8_10_is_applicable %}
{%tr if rear_parking_light_present %} -> {%tr if a_8_1_rear_parking_lights_present %}
{%tr if not rear_parking_light_present %} -> {%tr if not a_8_1_rear_parking_lights_present %}
{%tr if rear_fog_present %} -> {%tr if a_8_13_is_applicable %}
{%tr if not rear_fog_present %} -> {%tr if not a_8_13_is_applicable %}
{%tr if daytime_running_light_present %} -> {%tr if a_8_27_is_applicable %}
{%tr if not daytime_running_light_present %} -> {%tr if not a_8_27_is_applicable %}
{%tr if adaptive_front_lighting_present %} -> {%tr if a_8_7_is_applicable %}
{%tr if not adaptive_front_lighting_present %} -> {%tr if not a_8_7_is_applicable %}
{%tr if winter_tires_present %} -> {%tr if a_10_7_3_is_applicable %}
{%tr if a_21_7_numeric %} -> {%tr if a_21_7_is_numeric %}
{%tr if a_21_8_numeric %} -> {%tr if a_21_8_is_numeric %}
{%tr if a_23_1_electric %} -> {%tr if a_23_1_is_electric %}
```

`{%tr else %}` and `{%tr endif %}` are retained unchanged. Front and rear parking-light row conditions use distinct aliases because their presence flags are separate.

For A.8.13.2, `applicable_8_13_2` is a legacy full-result value in the present-lamp branch, while `rear_fog_a_8_13_2_status` is a pure status. Both map to separate canonical fields. When building context aliases, prefer `rear_fog_a_8_13_2_conclusion` for `a_8_13_2_conclusion`; it gives the correct `-` conclusion when the lamps are absent.

## Measurement and calculated-value placeholders

### Clause measurements

```text
{{ additional_brake_signal_count_value }} -> {{ a_8_1_additional_brake_signal_count_value }}
{{ high_beam_count_value }} -> {{ a_8_1_high_beam_count_value }}
{{ plate_light_count_value }} -> {{ a_8_1_plate_light_count_value }}
{{ rear_fog_count_value }} -> {{ a_8_1_rear_fog_count_value }}
{{ reverse_light_count_value }} -> {{ a_8_1_reverse_light_count_value }}
{{ light_device_conclusion }} -> {{ a_8_1_conclusion }}
{{ fog_light_left_distance_8_10_1 }} -> {{ a_8_10_1_left_distance_value }}
{{ fog_light_right_distance_8_10_1 }} -> {{ a_8_10_1_right_distance_value }}
{{ fog_light_lower_point_8_10_2 }} -> {{ a_8_10_2_lower_point_value }}
{{ fog_light_upper_point_8_10_2 }} -> {{ a_8_10_2_upper_point_value }}
{{ rear_fog_upper_point_8_13_2 }} -> {{ a_8_13_2_upper_point_value }}
{{ rear_fog_lower_point_8_13_2 }} -> {{ a_8_13_2_lower_point_value }}
{{ brake_signal_left_distance_mm }} -> {{ a_8_12_1_left_distance_value }}
{{ brake_signal_right_distance_mm }} -> {{ a_8_12_1_right_distance_value }}
{{ brake_signal_lower_point_mm }} -> {{ a_8_12_2_lower_point_value }}
{{ brake_signal_upper_point_mm }} -> {{ a_8_12_2_upper_point_value }}
{{ additional_brake_signal_from_glass_edge_mm }} -> {{ a_8_12_3_glass_edge_distance_value }}
{{ additional_brake_signal_from_support_surface_mm }} -> {{ a_8_12_3_support_surface_distance_value }}
{{ additional_brake_signal_optical_center_shift_mm }} -> {{ a_8_12_4_optical_center_shift_value }}
{{ turn_signal_frequency_hz }} -> {{ a_8_22_turn_signal_frequency_hz_value }}
{{ turn_signal_frequency_per_min }} -> {{ a_8_22_turn_signal_frequency_per_min_value }}
{{ low_beam_upper_point_mm }} -> {{ a_8_9_upper_point_value }}
{{ low_beam_lower_point_mm }} -> {{ a_8_9_lower_point_value }}
{{ left_34v_cd }} -> {{ a_8_20_6_left_34v_value }}
{{ right_34v_cd }} -> {{ a_8_20_6_right_34v_value }}
{{ left_52h_cd }} -> {{ a_8_20_6_left_52h_value }}
{{ right_52h_cd }} -> {{ a_8_20_6_right_52h_value }}
{{ calc_total_high_beam_cd }} -> {{ a_8_20_7_total_high_beam_value }}
{{ left_high_beam_cd }} -> {{ a_8_20_7_left_high_beam_value }}
{{ right_high_beam_cd }} -> {{ a_8_20_7_right_high_beam_value }}
{{ glass_transparency_windshield_pct }} -> {{ a_4_3_windshield_transparency_value }}
{{ glass_transparency_right_pct }} -> {{ a_4_3_right_transparency_value }}
{{ glass_transparency_left_pct }} -> {{ a_4_3_left_transparency_value }}
{{ axle_1_brake_difference_pct }} -> {{ a_5_1_1_4_axle_1_difference_value }}
{{ axle_2_brake_difference_pct }} -> {{ a_5_1_1_4_axle_2_difference_value }}
{{ calc_service_brake_specific_force }} -> {{ a_5_1_4_1_1_service_specific_force_value }}
{{ calc_parking_brake_specific_force }} -> {{ a_5_1_4_2_1_parking_specific_force_value }}
{{ service_brake_control_force_axle1_n }} -> {{ a_5_1_1_1_axle_1_control_force_value }}
{{ service_brake_control_force_axle2_n }} -> {{ a_5_1_1_1_axle_2_control_force_value }}
{{ parking_brake_control_force_n }} -> {{ a_5_1_5_parking_control_force_value }}
{{ steering_backlash_deg }} -> {{ a_2_3_steering_backlash_value }}
{{ bumper_to_body_distance_mm }} -> {{ a_16_7_bumper_to_body_distance_value }}
{{ protruding_elements_doors_mm }} -> {{ a_16_9_doors_protrusion_value }}
{{ protruding_elements_other_mm }} -> {{ a_16_9_other_protrusion_value }}
{{ actual_speed_kmh }} -> {{ a_12_3_actual_speed_value }}
{{ speed_by_speedometer_kmh }} -> {{ a_12_3_speedometer_speed_value }}
{{ co_min_21_7_with_unit }} -> {{ a_21_7_co_min_value }}
{{ co_max_21_7_with_unit }} -> {{ a_21_7_co_max_value }}
{{ light_absorption_avg_21_8_with_unit }} -> {{ a_21_8_light_absorption_average_value }}
{{ exhaust_noise_constant_db }} -> {{ a_23_1_constant_noise_value }}
{{ exhaust_noise_deceleration_db }} -> {{ a_23_1_deceleration_noise_value }}
{{ tire_depth_fl_10_7_2 }} -> {{ a_10_7_2_front_left_tread_depth_value }}
{{ tire_depth_fr_10_7_2 }} -> {{ a_10_7_2_front_right_tread_depth_value }}
{{ tire_depth_rl_10_7_2 }} -> {{ a_10_7_2_rear_left_tread_depth_value }}
{{ tire_depth_rr_10_7_2 }} -> {{ a_10_7_2_rear_right_tread_depth_value }}
{{ tire_depth_fl_10_7_3 }} -> {{ a_10_7_3_front_left_tread_depth_value }}
{{ tire_depth_fr_10_7_3 }} -> {{ a_10_7_3_front_right_tread_depth_value }}
{{ tire_depth_rl_10_7_3 }} -> {{ a_10_7_3_rear_left_tread_depth_value }}
{{ tire_depth_rr_10_7_3 }} -> {{ a_10_7_3_rear_right_tread_depth_value }}
{{ sun_strip_width_11_8 }} -> {{ a_11_8_sun_strip_width_value }}
```

### Shared vehicle, protocol, and test-condition fields

```text
{{ protocol_number }} -> {{ protocol_number }}
{{ protocol_date }} -> {{ protocol_date }}
{{ owner_first_name }} -> {{ owner_first_name }}
{{ owner_last_name }} -> {{ owner_last_name }}
{{ owner_middle_name }} -> {{ owner_middle_name }}
{{ manufacturer_info }} -> {{ vehicle_manufacturer_info }}
{{ brand_name }} -> {{ vehicle_brand_name }}
{{ commercial_name }} -> {{ vehicle_model_name }}
{{ body_type }} -> {{ vehicle_body_type }}
{{ vin }} -> {{ vehicle_vin }}
{{ registration_number }} -> {{ vehicle_registration_number }}
{{ vehicle_category }} -> {{ vehicle_category }}
{{ vehicle_length_mm }} -> {{ vehicle_length_value }}
{{ vehicle_width_mm }} -> {{ vehicle_width_value }}
{{ vehicle_height_mm }} -> {{ vehicle_height_value }}
{{ ambient_temperature_c }} -> {{ test_conditions_ambient_temperature_value }}
{{ relative_humidity_pct }} -> {{ test_conditions_relative_humidity_value }}
{{ atmospheric_pressure_kpa }} -> {{ test_conditions_atmospheric_pressure_value }}
{{ road_ambient_temperature_c }} -> {{ road_conditions_temperature_value }}
{{ road_relative_humidity_pct }} -> {{ road_conditions_relative_humidity_value }}
{{ phase_a_n_voltage_v }} -> {{ power_supply_phase_a_n_voltage_value }}
{{ phase_b_n_voltage_v }} -> {{ power_supply_phase_b_n_voltage_value }}
{{ phase_c_n_voltage_v }} -> {{ power_supply_phase_c_n_voltage_value }}
{{ phase_ab_voltage_v }} -> {{ power_supply_phase_ab_voltage_value }}
{{ phase_bc_voltage_v }} -> {{ power_supply_phase_bc_voltage_value }}
{{ phase_ac_voltage_v }} -> {{ power_supply_phase_ac_voltage_value }}
{{ photo_gas_test }} -> {{ photo_gas_test }}
{{ photo_noise_test }} -> {{ photo_noise_test }}
{{ photo_stand_test }} -> {{ photo_stand_test }}
```

### Remaining measurement/calculation values

```text
{{ u_actual_speed_kmh }} -> {{ a_12_3_actual_speed_uncertainty }}
{{ u_axle_1_brake_difference_pct }} -> {{ a_5_1_1_4_axle_1_difference_uncertainty }}
{{ u_axle_2_brake_difference_pct }} -> {{ a_5_1_1_4_axle_2_difference_uncertainty }}
{{ u_bumper_to_body_distance_mm }} -> {{ a_16_7_bumper_to_body_distance_uncertainty }}
{{ u_brake_signal_left_distance_mm }} -> {{ a_8_12_1_left_distance_uncertainty }}
{{ u_brake_signal_right_distance_mm }} -> {{ a_8_12_1_right_distance_uncertainty }}
{{ u_brake_signal_lower_point_mm }} -> {{ a_8_12_2_lower_point_uncertainty }}
{{ u_brake_signal_upper_point_mm }} -> {{ a_8_12_2_upper_point_uncertainty }}
{{ u_additional_brake_signal_from_glass_edge_mm }} -> {{ a_8_12_3_glass_edge_distance_uncertainty }}
{{ u_additional_brake_signal_from_support_surface_mm }} -> {{ a_8_12_3_support_surface_distance_uncertainty }}
{{ u_additional_brake_signal_optical_center_shift_mm }} -> {{ a_8_12_4_optical_center_shift_uncertainty }}
{{ u_calc_total_high_beam_cd }} -> {{ a_8_20_7_total_high_beam_uncertainty }}
{{ u_glass_transparency_windshield_pct }} -> {{ a_4_3_windshield_transparency_uncertainty }}
{{ u_glass_transparency_right_pct }} -> {{ a_4_3_right_transparency_uncertainty }}
{{ u_glass_transparency_left_pct }} -> {{ a_4_3_left_transparency_uncertainty }}
{{ u_left_34v_cd }} -> {{ a_8_20_6_left_34v_uncertainty }}
{{ u_right_34v_cd }} -> {{ a_8_20_6_right_34v_uncertainty }}
{{ u_left_52h_cd }} -> {{ a_8_20_6_left_52h_uncertainty }}
{{ u_right_52h_cd }} -> {{ a_8_20_6_right_52h_uncertainty }}
{{ u_low_beam_upper_point_mm }} -> {{ a_8_9_upper_point_uncertainty }}
{{ u_low_beam_lower_point_mm }} -> {{ a_8_9_lower_point_uncertainty }}
{{ u_parking_brake_control_force_n }} -> {{ a_5_1_5_parking_control_force_uncertainty }}
{{ u_parking_brake_specific_force }} -> {{ a_5_1_4_2_1_parking_specific_force_uncertainty }}
{{ u_service_brake_control_force_axle1_n }} -> {{ a_5_1_1_1_axle_1_control_force_uncertainty }}
{{ u_service_brake_control_force_axle2_n }} -> {{ a_5_1_1_1_axle_2_control_force_uncertainty }}
{{ u_service_brake_specific_force }} -> {{ a_5_1_4_1_1_service_specific_force_uncertainty }}
{{ u_steering_backlash_deg }} -> {{ a_2_3_steering_backlash_uncertainty }}
{{ u_protruding_elements_doors_mm }} -> {{ a_16_9_doors_protrusion_uncertainty }}
{{ u_protruding_elements_other_mm }} -> {{ a_16_9_other_protrusion_uncertainty }}
{{ u_turn_signal_frequency_hz }} -> {{ a_8_22_turn_signal_frequency_hz_uncertainty }}
{{ u_turn_signal_frequency_per_min }} -> {{ a_8_22_turn_signal_frequency_per_min_uncertainty }}
{{ u_vehicle_length_mm }} -> {{ vehicle_length_uncertainty }}
{{ u_vehicle_width_mm }} -> {{ vehicle_width_uncertainty }}
{{ u_vehicle_height_mm }} -> {{ vehicle_height_uncertainty }}
```

### Counts, intensities, common rows, and miscellaneous

```text
{{ mileage_21_9 }} -> {{ a_21_9_status }}
```

> Measurement fields reused across multiple clauses (vehicle dimensions, glass values, selected calculated brake values) are intentionally mapped to shared measurement aliases above. Review these shared-field mappings before any bulk rename.

## Migration Notes

- This is a proposed name map, not an edit script. No v5 placeholders were changed.
- Canonical status and conclusion aliases should be emitted alongside legacy aliases first.
- V5 should be migrated and rendered/verified before changing the old template.
- Several source names are duplicated by role (for example, `applicable_21_9` and `mileage_21_9`) and should collapse to a single canonical status in the migrated template.
