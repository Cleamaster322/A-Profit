const NUMERIC_RANGE_RULES = {
    ambient_temp_c: {min: 18, max: 22, label: "Температура окружающей среды", unit: "°C"},
    ambient_humidity_pct: {min: 45, max: 69, label: "Относительная влажность", unit: "%"},
    atmospheric_pressure_kpa: {min: 92, max: 105, label: "Атмосферное давление", unit: "кПа"},
    road_ambient_temp_c: {min: -25, max: 40, label: "Температура окружающей среды на дороге", unit: "°C"},
    road_ambient_humidity_pct: {min: 15, max: 95, label: "Относительная влажность на дороге", unit: "%"},
    electric_frequency_hz: {min: 50, max: 50, label: "Частота электрической сети", unit: "Гц"},
    voltage_phase_a_zero: {min: 187, max: 242, label: "Фаза A–N", unit: "В"},
    voltage_phase_b_zero: {min: 187, max: 242, label: "Фаза B–N", unit: "В"},
    voltage_phase_c_zero: {min: 187, max: 242, label: "Фаза C–N", unit: "В"},
    voltage_phase_ab: {min: 332, max: 418, label: "Фаза A–B", unit: "В"},
    voltage_phase_bc: {min: 332, max: 418, label: "Фаза B–C", unit: "В"},
    voltage_phase_ac: {min: 332, max: 418, label: "Фаза A–C", unit: "В"},
    service_brake_control_force_axle1_n: {min: 0, max: 490, label: "Усилие на органе рабочей тормозной системы, ось 1", unit: "Н"},
    service_brake_control_force_axle2_n: {min: 0, max: 490, label: "Усилие на органе рабочей тормозной системы, ось 2", unit: "Н"},
    service_brake_front_left_kn: {min: 0, max: 30, label: "Тормозная сила переднего левого колеса", unit: "кН"},
    service_brake_front_right_kn: {min: 0, max: 30, label: "Тормозная сила переднего правого колеса", unit: "кН"},
    service_brake_rear_left_kn: {min: 0, max: 30, label: "Тормозная сила заднего левого колеса", unit: "кН"},
    service_brake_rear_right_kn: {min: 0, max: 30, label: "Тормозная сила заднего правого колеса", unit: "кН"},
    parking_brake_left_kn: {min: 0, max: 30, label: "Тормозная сила стояночной системы, левое колесо", unit: "кН"},
    parking_brake_right_kn: {min: 0, max: 30, label: "Тормозная сила стояночной системы, правое колесо", unit: "кН"},
    stand_axle1_load_kg: {min: 0, max: 3500, label: "Нагрузка на ось 1 на тормозном стенде", unit: "кг"},
    stand_axle2_load_kg: {min: 0, max: 3500, label: "Нагрузка на ось 2 на тормозном стенде", unit: "кг"},
    bumper_to_body_distance_mm: {min: 0, max: 20, label: "Расстояние от края бампера до кузова", unit: "мм"},
    sun_strip_width_mm: {min: 0, max: 140, label: "Ширина светозащитной полосы", unit: "мм"},
    speed_by_speedometer_kmh: {min: 21, max: 21, label: "Скорость по спидометру", unit: "км/ч"},
    actual_speed_kmh: {min: 20, max: 20, label: "Фактическая скорость", unit: "км/ч"},
    exhaust_noise_constant_db: {min: 0, max: 96, label: "Шум на постоянных оборотах", unit: "дБА"},
    exhaust_noise_deceleration_db: {min: 0, max: 96, label: "Шум при замедлении", unit: "дБА"},
    co_min_pct: {min: 0, max: 0.3, label: "CO на минимальных оборотах", unit: "%"},
    co_max_pct: {min: 0, max: 0.2, label: "CO на повышенных оборотах", unit: "%"},
    light_absorption_1: {min: 0, max: 1.5, label: "Дымность, замер 1", unit: "м⁻¹"},
    light_absorption_2: {min: 0, max: 1.5, label: "Дымность, замер 2", unit: "м⁻¹"},
    light_absorption_3: {min: 0, max: 1.5, label: "Дымность, замер 3", unit: "м⁻¹"},
    light_absorption_4: {min: 0, max: 1.5, label: "Дымность, замер 4", unit: "м⁻¹"},
    light_absorption_5: {min: 0, max: 1.5, label: "Дымность, замер 5", unit: "м⁻¹"},
    light_absorption_6: {min: 0, max: 1.5, label: "Дымность, замер 6", unit: "м⁻¹"},
    protruding_elements_doors_mm: {min: 0, max: 40, label: "Выступание ручек дверей и багажника", unit: "мм"},
    protruding_elements_other_mm: {min: 0, max: 30, label: "Выступание остальных элементов", unit: "мм"},
    vehicle_length_mm: {min: 0, max: 8150, label: "Длина транспортного средства", unit: "мм"},
    vehicle_width_mm: {min: 0, max: 4500, label: "Ширина транспортного средства", unit: "мм"},
    vehicle_height_mm: {min: 0, max: 2800, label: "Высота транспортного средства", unit: "мм"},
    vehicle_weight_kg: {min: 200, max: 3500, label: "Масса при взвешивании на весах", unit: "кг"},
    axle1_load_kg: {min: 200, max: 3500, label: "Нагрузка на ось 1 при взвешивании на весах", unit: "кг"},
    axle2_load_kg: {min: 200, max: 3500, label: "Нагрузка на ось 2 при взвешивании на весах", unit: "кг"},
    low_beam_count: {min: 2, max: 2, allowedValues: [2], label: "Фара ближнего света", unit: "шт."},
    high_beam_count: {min: 2, max: 4, allowedValues: [2, 4], label: "Фара дальнего света", unit: "шт."},
    front_fog_count: {min: 2, max: 2, allowedValues: [2], label: "Передние противотуманные фары", unit: "шт."},
    reverse_light_count: {min: 1, max: 2, allowedValues: [1, 2], label: "Фонарь заднего хода", unit: "шт."},
    turn_signal_count: {min: 2, max: 6, allowedValues: [2, 4, 6], label: "Указатели поворота", unit: "шт."},
    front_position_light_count: {min: 2, max: 2, allowedValues: [2], label: "Передние габаритные огни", unit: "шт."},
    rear_position_light_count: {min: 2, max: 2, allowedValues: [2], label: "Задние габаритные огни", unit: "шт."},
    main_brake_signal_count: {min: 2, max: 2, allowedValues: [2], label: "Основной сигнал торможения", unit: "шт."},
    additional_brake_signal_count: {min: 1, max: 2, allowedValues: [1, 2], label: "Дополнительный сигнал торможения", unit: "шт."},
    rear_fog_count: {min: 0, max: 2, allowedValues: [0, 1, 2], label: "Задние противотуманные фонари", unit: "шт."},
    plate_light_count: {min: 1, max: 2, allowedValues: [1, 2], label: "Фонарь освещения заднего номера", unit: "шт."},
    daytime_running_light_count: {min: 2, max: 2, allowedValues: [2], label: "Дневные ходовые огни", unit: "шт."},
    parking_light_count: {min: 2, max: 2, allowedValues: [2], label: "Передние стояночные огни", unit: "шт."},
    rear_parking_light_count: {min: 2, max: 2, allowedValues: [2], label: "Задние стояночные огни", unit: "шт."},
    adaptive_front_lighting_count: {min: 2, max: 2, allowedValues: [2], label: "Адаптивная система переднего освещения", unit: "шт."},
    brake_signal_left_distance_mm: {min: 0, max: 400, label: "Основной сигнал торможения, левый по ширине", unit: "мм"},
    brake_signal_right_distance_mm: {min: 0, max: 400, label: "Основной сигнал торможения, правый по ширине", unit: "мм"},
    brake_signal_upper_point_mm: {min: 350, max: 1500, label: "Основной сигнал торможения, верхняя точка", unit: "мм"},
    brake_signal_lower_point_mm: {min: 350, max: 1500, label: "Основной сигнал торможения, нижняя точка", unit: "мм"},
    additional_brake_signal_from_support_surface_mm: {min: 850, max: 2800, label: "Дополнительный сигнал торможения от опорной поверхности", unit: "мм"},
    additional_brake_signal_from_glass_edge_mm: {min: 0, max: 150, label: "Дополнительный сигнал торможения от края стекла", unit: "мм"},
    additional_brake_signal_optical_center_shift_mm: {min: 0, max: 150, label: "Смещение центра дополнительного сигнала торможения", unit: "мм"},
    rear_fog_upper_point_mm: {min: 250, max: 1000, label: "Задние противотуманные фонари, верхняя точка", unit: "мм"},
    rear_fog_lower_point_mm: {min: 250, max: 1000, label: "Задние противотуманные фонари, нижняя точка", unit: "мм"},
    turn_signal_frequency_hz: {min: 1.4, max: 1.6, allowedValues: [1.4, 1.6], label: "Частота указателей поворота", unit: "Гц"},
    turn_signal_frequency_per_min: {min: 84, max: 96, allowedValues: [84, 96], label: "Частота указателей поворота", unit: "проблесков/мин"},
};

const TIRE_DEPTH_FIELDS = new Set([
    "tire_depth_fl_mm",
    "tire_depth_fr_mm",
    "tire_depth_rl_mm",
    "tire_depth_rr_mm",
]);

function getNumericRule(fieldName, form) {
    if (TIRE_DEPTH_FIELDS.has(fieldName)) {
        if (form.tire_season === "summer") {
            return {min: 1.6, max: 10, label: "Глубина протектора летней шины", unit: "мм"};
        }
        if (form.tire_season === "winter") {
            return {min: 4, max: 10, label: "Глубина протектора зимней шины", unit: "мм"};
        }
        return null;
    }

    if (fieldName === "axle_1_brake_difference_pct") {
        const max = form.service_brake_type === "disc_disc" || form.service_brake_type === "disc_drum" ? 20 : 25;
        return {min: 0, max, label: "Относительная разность тормозных сил колес оси 1", unit: "%"};
    }

    if (fieldName === "axle_2_brake_difference_pct") {
        const max = form.service_brake_type === "disc_disc" ? 20 : 25;
        return {min: 0, max, label: "Относительная разность тормозных сил колес оси 2", unit: "%"};
    }

    if (fieldName === "parking_brake_control_force_n") {
        if (form.parking_brake_type === "mechanical_hand") {
            return {min: 0, max: 392, label: "Усилие на ручном органе стояночной тормозной системы", unit: "Н"};
        }
        if (form.parking_brake_type === "mechanical_pedal") {
            return {min: 0, max: 490, label: "Усилие на ножном органе стояночной тормозной системы", unit: "Н"};
        }
        return null;
    }

    return NUMERIC_RANGE_RULES[fieldName] ?? null;
}

function parseNumericValue(rawValue) {
    if (rawValue === null || rawValue === undefined) return null;
    const text = String(rawValue).trim();
    if (!text || text === "-") return null;
    const normalized = text.replace(/\s/g, "").replace(",", ".");
    const value = Number(normalized);
    return Number.isFinite(value) ? value : Number.NaN;
}

function formatBound(value) {
    return String(value).replace(".", ",");
}

export function getNumericRangeError(fieldName, form) {
    const rule = getNumericRule(fieldName, form);
    if (!rule) return "";

    const rawValue = form[fieldName];
    const value = parseNumericValue(rawValue);
    if (value === null) return "";

    const range = `от ${formatBound(rule.min)} до ${formatBound(rule.max)} ${rule.unit}`;
    if (!Number.isFinite(value)) {
        return `${rule.label}: введите число; допустимый диапазон ${range}.`;
    }
    const allowedValues = rule.allowedValues;
    if (value < rule.min || value > rule.max || (allowedValues && !allowedValues.includes(value))) {
        const allowedText = allowedValues
            ? ` Допустимые варианты: ${allowedValues.map(formatBound).join(" или ")}.`
            : "";
        return `${rule.label}: допустимый диапазон ${range}.${allowedText}`;
    }
    return "";
}

export function validateProtocolNumericRanges(form) {
    const errors = [];
    for (const fieldName of Object.keys(NUMERIC_RANGE_RULES)) {
        const message = getNumericRangeError(fieldName, form);
        if (message) errors.push({fieldName, message});
    }
    for (const fieldName of TIRE_DEPTH_FIELDS) {
        const message = getNumericRangeError(fieldName, form);
        if (message) errors.push({fieldName, message});
    }
    const actual = parseNumericValue(form.actual_speed_kmh);
    const speedometer = parseNumericValue(form.speed_by_speedometer_kmh);
    if (actual !== null && speedometer !== null && Number.isFinite(actual) && Number.isFinite(speedometer) && actual >= speedometer) {
        errors.push({
            fieldName: "actual_speed_kmh",
            message: "Фактическая скорость должна быть меньше скорости по спидометру.",
        });
    }
    return errors;
}
