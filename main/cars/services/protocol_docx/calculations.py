from decimal import Decimal

from .formatters import decimal_value, fmt_num, safe_div

K_95 = Decimal("1.65")
SQRT_3 = Decimal("3").sqrt()
G = Decimal("9.8")


# =========================
# Базовые helpers
# =========================

def get_related_safe(obj, attr_name):
    if obj is None:
        return None

    try:
        return getattr(obj, attr_name)
    except Exception:
        return None


def get_value(obj, attr_name):
    if obj is None:
        return None

    return getattr(obj, attr_name, None)


def sum_decimal(*values):
    result = Decimal("0")
    has_any = False

    for value in values:
        number = decimal_value(value)

        if number is not None:
            result += number
            has_any = True

    if not has_any:
        return None

    return result


def root_sum_squares(*values):
    """
    sqrt(x1^2 + x2^2 + ...)
    """
    total = Decimal("0")
    has_any = False

    for value in values:
        number = decimal_value(value)

        if number is not None:
            total += number * number
            has_any = True

    if not has_any:
        return None

    return total.sqrt()


def standard_uncertainty_from_abs_error(abs_error):
    """
    u = Δ / sqrt(3)
    """
    abs_error = decimal_value(abs_error)

    if abs_error is None:
        return None

    return abs_error / SQRT_3


def standard_uncertainty_from_relative_error(value, percent):
    """
    u = (value * percent / 100) / sqrt(3)
    """
    value = decimal_value(value)
    percent = decimal_value(percent)

    if value is None or percent is None:
        return None

    abs_error = value * percent / Decimal("100")

    return standard_uncertainty_from_abs_error(abs_error)


def expanded_from_standard(standard_uncertainty):
    """
    U = k * u
    """
    standard_uncertainty = decimal_value(standard_uncertainty)

    if standard_uncertainty is None:
        return None

    return K_95 * standard_uncertainty


def expanded_uncertainty_from_abs_error(abs_error):
    """
    U = k * (Δ / sqrt(3))
    """
    standard_u = standard_uncertainty_from_abs_error(abs_error)
    return expanded_from_standard(standard_u)


def expanded_uncertainty_from_relative_error(value, percent):
    """
    U = k * ((value * percent / 100) / sqrt(3))
    """
    standard_u = standard_uncertainty_from_relative_error(value, percent)
    return expanded_from_standard(standard_u)


def get_vehicle_mass_for_brake_calc(measurement):
    """
    Масса для расчета удельной тормозной силы.

    Приоритет:
    1) сумма нагрузок на ось по весам;
    2) масса ТС;
    3) None, если данных нет.
    """
    axle_mass_kg = sum_decimal(
        get_value(measurement, "axle1_load_kg"),
        get_value(measurement, "axle2_load_kg"),
    )

    if axle_mass_kg is not None and axle_mass_kg != 0:
        return axle_mass_kg

    vehicle_weight_kg = decimal_value(
        get_value(measurement, "vehicle_weight_kg")
    )

    if vehicle_weight_kg is not None and vehicle_weight_kg != 0:
        return vehicle_weight_kg

    return None


# =========================
# Расчётные значения
# =========================

def calc_service_brake_specific_force(brake, measurement):
    """
    Удельная тормозная сила рабочей тормозной системы.

    Z = F_sum / W

    F_sum — сумма тормозных сил, кН.
    W — вес ТС, кН.

    Массу берем так:
    1) axle1_load_kg + axle2_load_kg;
    2) если нагрузок на оси нет — vehicle_weight_kg.
    """
    brake_sum_kn = sum_decimal(
        get_value(brake, "service_brake_front_left_kn"),
        get_value(brake, "service_brake_front_right_kn"),
        get_value(brake, "service_brake_rear_left_kn"),
        get_value(brake, "service_brake_rear_right_kn"),
    )

    mass_kg = get_vehicle_mass_for_brake_calc(measurement)

    if brake_sum_kn is None or mass_kg is None or mass_kg == 0:
        return None

    weight_kn = mass_kg * G / Decimal("1000")

    return safe_div(brake_sum_kn, weight_kn)


def calc_parking_brake_specific_force(brake, measurement):
    """
    Удельная тормозная сила стояночной тормозной системы.

    Z = F_sum / W

    F_sum — сумма тормозных сил, кН.
    W — вес ТС, кН.

    Массу берем так:
    1) axle1_load_kg + axle2_load_kg;
    2) если нагрузок на оси нет — vehicle_weight_kg.
    """
    brake_sum_kn = sum_decimal(
        get_value(brake, "parking_brake_left_kn"),
        get_value(brake, "parking_brake_right_kn"),
    )

    mass_kg = get_vehicle_mass_for_brake_calc(measurement)

    if brake_sum_kn is None or mass_kg is None or mass_kg == 0:
        return None

    weight_kn = mass_kg * G / Decimal("1000")

    return safe_div(brake_sum_kn, weight_kn)


def calc_total_high_beam_cd(light):
    return sum_decimal(
        get_value(light, "left_high_beam_cd"),
        get_value(light, "right_high_beam_cd"),
    )


def calc_light_absorption_average(measurement):
    values = [
        decimal_value(get_value(measurement, "light_absorption_1")),
        decimal_value(get_value(measurement, "light_absorption_2")),
        decimal_value(get_value(measurement, "light_absorption_3")),
        decimal_value(get_value(measurement, "light_absorption_4")),
        decimal_value(get_value(measurement, "light_absorption_5")),
        decimal_value(get_value(measurement, "light_absorption_6")),
    ]

    values = [value for value in values if value is not None]

    if not values:
        return None

    return sum(values) / Decimal(len(values))


def standard_uncertainty_type_a(values):
    """Type A standard uncertainty of the mean for repeated measurements."""
    values = [decimal_value(value) for value in values]
    values = [value for value in values if value is not None]

    if len(values) < 2:
        return None

    mean = sum(values) / Decimal(len(values))
    squared_deviations = sum((value - mean) ** 2 for value in values)
    count = Decimal(len(values))

    return (squared_deviations / (count * (count - Decimal("1")))).sqrt()


def calc_light_absorption_uncertainty(measurement):
    """Expanded uncertainty from type A and type B components.

    The updated workbook uses six repeated readings when available:
    uA = sqrt(sum((xi - mean)^2) / (n * (n - 1)))
    uB = sqrt((0.05 / sqrt(3))^2 + (0.001 / (2 * sqrt(3)))^2)
    U = 1.65 * sqrt(uA^2 + uB^2)
    """
    values = [
        get_value(measurement, f"light_absorption_{index}")
        for index in range(1, 7)
    ]
    type_a = standard_uncertainty_type_a(values)
    type_b_instrument = standard_uncertainty_from_abs_error(Decimal("0.05"))
    type_b_resolution = Decimal("0.001") / (Decimal("2") * SQRT_3)
    type_b = root_sum_squares(type_b_instrument, type_b_resolution)

    if type_a is None:
        return expanded_from_standard(type_b)

    combined = root_sum_squares(type_a, type_b)
    return expanded_from_standard(combined)


def build_calculated_values(protocol):
    measurement = get_related_safe(protocol, "measurement")
    brake = get_related_safe(protocol, "brake")
    light = get_related_safe(protocol, "light")

    service_specific = calc_service_brake_specific_force(brake, measurement)
    parking_specific = calc_parking_brake_specific_force(brake, measurement)
    total_high_beam = calc_total_high_beam_cd(light)
    light_absorption_average = calc_light_absorption_average(measurement)

    return {
        "calc_service_brake_specific_force": fmt_num(service_specific, 2),
        "calc_parking_brake_specific_force": fmt_num(parking_specific, 2),
        "calc_total_high_beam_cd": fmt_num(total_high_beam, 1),
        "calc_light_absorption_average": fmt_num(light_absorption_average, 2),
    }


# =========================
# Базовые неопределенности
# =========================

def u_co_pct():
    """
    CO:
    Δ = ±0.03 %
    U = 1.65 * 0.03 / sqrt(3) = 0.0286 ≈ 0.03 %
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.03"))


def u_noise_db():
    """
    Шум:
    Δ = ±0.5 дБА
    U = 1.65 * 0.5 / sqrt(3) = 0.476 ≈ 0.5 дБА
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_abs_error(Decimal("0.5")),
        Decimal("0.1") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def u_steering_backlash_deg():
    """
    Люфт рулевого управления:
    Δ = ±0.5°
    U = 1.65 * 0.5 / sqrt(3) = 0.476 ≈ 0.5°
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_abs_error(Decimal("0.5")),
        Decimal("0.1") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def linear_abs_error_by_value_mm(value):
    """
    Автоматический выбор абсолютной погрешности линейного измерения
    по диапазону измеренного значения.

    Используется для геометрических размеров световых приборов.

    Диапазоны:
    0–9 мм        -> Δ = 0.15 мм
    10–99 мм      -> Δ = 0.20 мм
    100–5000 мм   -> Δ = 0.30 мм

    Даже если в исходной таблице верхний диапазон указан до 2 м,
    в проекте принимаем диапазон до 5000 мм.
    """
    value = decimal_value(value)

    if value is None:
        return None

    value = abs(value)

    if value <= Decimal("9"):
        return Decimal("0.15")

    if value <= Decimal("99"):
        return Decimal("0.20")

    return Decimal("0.30")

def rgk_r5_vehicle_abs_error_mm(value):
    """
    Абсолютная погрешность рулетки RGK R-5 для габаритных размеров ТС.

    Логика по Excel:
    - значение до 1 м:
        0–9 мм      -> Δ = 0.15 мм
        10–99 мм    -> Δ = 0.20 мм
        100–999 мм  -> Δ = 0.30 мм

    - значение от 1 м и выше:
        Δ = 0.3 + 0.15 * (N - 1)

      где N — нижняя граница метрового интервала.

      Примеры:
      1435 мм -> интервал 1–2 м -> N = 1 -> Δ = 0.30 мм
      1780 мм -> интервал 1–2 м -> N = 1 -> Δ = 0.30 мм
      4640 мм -> интервал 4–5 м -> N = 4 -> Δ = 0.75 мм
    """
    value = decimal_value(value)

    if value is None:
        return None

    value = abs(value)

    if value <= Decimal("9"):
        return Decimal("0.15")

    if value <= Decimal("99"):
        return Decimal("0.20")

    if value < Decimal("1000"):
        return Decimal("0.30")

    meters_floor = int(value // Decimal("1000"))

    if meters_floor < 1:
        meters_floor = 1

    return Decimal("0.3") + Decimal("0.15") * (Decimal(meters_floor) - Decimal("1"))


def u_rgk_r5_vehicle_mm(value):
    """
    Расширенная неопределенность габаритного размера ТС.

    U = 1.65 * Δ / sqrt(3)
    """
    abs_error = rgk_r5_vehicle_abs_error_mm(value)

    if abs_error is None:
        return None

    return expanded_uncertainty_from_abs_error(abs_error)

def u_linear_by_value_mm(value):
    """
    Расширенная неопределенность линейного измерения
    с автоматическим выбором базы Δ.

    U = 1.65 * Δ / sqrt(3)

    Примеры:
    value = 0 мм:
        Δ = 0.15 мм
        U = 1.65 * 0.15 / sqrt(3) = 0.1429... ≈ 0.14 мм

    value = 50 мм:
        Δ = 0.20 мм
        U = 1.65 * 0.20 / sqrt(3) = 0.1905... ≈ 0.19 мм

    value = 150 мм:
        Δ = 0.30 мм
        U = 1.65 * 0.30 / sqrt(3) = 0.2857... ≈ 0.29 мм
    """
    abs_error = linear_abs_error_by_value_mm(value)

    if abs_error is None:
        return None

    return expanded_uncertainty_from_abs_error(abs_error)


def u_linear_03_mm():
    """
    Фиксированная линейная неопределенность:
    Δ = ±0.3 мм
    U = 1.65 * 0.3 / sqrt(3) = 0.286 ≈ 0.29 мм

    Оставлена для тех пунктов, где по Excel/методике нужна именно
    фиксированная база 0.3 мм, а не автоподбор по диапазону.
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.3"))


def u_linear_02_mm():
    """
    Линейные измерения:
    Δ = ±0.2 мм

    Для ширины светозащитной полосы:
    U = 1.65 * 0.2 / sqrt(3) = 0.1905 ≈ 0.19 мм
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.2"))


def u_bumper_distance_mm():
    """
    Расстояние между краем бампера и кузовом.

    Excel:
    C1362 = E1344 * F1359
    E1344 = I1320 / sqrt(3)
    I1320 = 0.14 мм
    F1359 = 1.65

    U = 1.65 * 0.14 / sqrt(3) = 0.1333... ≈ 0.13 мм
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.14"))


def u_protruding_elements_mm():
    """
    Выступающие элементы: ручки дверей/багажника, остальные элементы.

    Excel:
    C1401 = F1398 * E1378
    E1378 = I1319 / sqrt(3)
    I1319 = 0.10 мм
    F1398 = 1.65

    U = 1.65 * 0.10 / sqrt(3) = 0.0952... ≈ 0.10 мм
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.10"))


def u_tire_depth_mm():
    """
    Остаточная глубина протектора:
    Δ = ±0.1 мм
    U = 1.65 * 0.1 / sqrt(3) = 0.095 ≈ 0.1 мм
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.1"))


def u_glass_transparency_pct():
    """
    Светопропускание стекол:
    Δ = ±2.0 %
    U = 1.65 * 2.0 / sqrt(3) = 1.905 ≈ 2.0 %
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_abs_error(Decimal("2.0")),
        Decimal("0.1") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def u_speed_kmh(value):
    """
    Неопределенность скорости ТС.

    Excel:
    u = V * δ / (100 * sqrt(3))
    U = 1.65 * u

    где:
    V — измеренная скорость, км/ч
    δ = 0.15 %

    Пример:
    V = 20 км/ч
    u = 20 * 0.15 / (100 * sqrt(3)) = 0.0173
    U = 1.65 * 0.0173 = 0.0286 ≈ 0.03 км/ч
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_relative_error(value, Decimal("0.15")),
        Decimal("0.1") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def u_turn_signal_frequency_hz():
    """
    Частота мерцания указателей поворота, Гц:
    Δ = ±0.1 Гц
    U = 1.65 * 0.1 / sqrt(3) = 0.095 ≈ 0.1 Гц
    """
    instrument = Decimal("0.1") / SQRT_3
    resolution = Decimal("0.1") / (Decimal("2") * SQRT_3)
    return expanded_from_standard(root_sum_squares(instrument, resolution))


def u_turn_signal_frequency_per_min():
    """
    Частота мерцания указателей поворота, проблесков/мин:
    U_min = U_hz * 60
    """
    value = u_turn_signal_frequency_hz()

    if value is None:
        return None

    return value * Decimal("60")


def u_light_absorption_m_1():
    """
    Коэффициент поглощения света:
    Δ = ±0.05 м-1
    U = 1.65 * 0.05 / sqrt(3) = 0.0476 ≈ 0.05 м-1
    """
    return expanded_uncertainty_from_abs_error(Decimal("0.05"))


# =========================
# Габариты, масса
# =========================

def u_vehicle_length_mm(value):
    """
    Неопределенность габаритной длины ТС.
    Средство измерения: рулетка RGK R-5.
    """
    return u_rgk_r5_vehicle_mm(value)


def u_vehicle_width_mm(value):
    """
    Неопределенность габаритной ширины ТС.
    Средство измерения: рулетка RGK R-5.
    """
    return u_rgk_r5_vehicle_mm(value)


def u_vehicle_height_mm(value):
    """
    Неопределенность габаритной высоты ТС.
    Средство измерения: рулетка RGK R-5.
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_abs_error(Decimal("2")),
        Decimal("1") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def u_scale_kg():
    """
    Масса и нагрузка на оси по весам:
    Δ = ±5 кг
    U = 1.65 * 5 / sqrt(3) = 4.763 ≈ 5 кг
    """
    standard_u = root_sum_squares(
        standard_uncertainty_from_abs_error(Decimal("5")),
        Decimal("5") / (Decimal("2") * SQRT_3),
    )
    return expanded_from_standard(standard_u)


def u_stand_load_kg(value):
    """
    Нагрузка на ось на тормозном стенде:
    относительная погрешность ±3 %

    U = 1.65 * ((value * 3 / 100) / sqrt(3))
    """
    return expanded_from_standard(standard_stand_load_kg(value))


# =========================
# Тормоза: неопределенности
# =========================

def u_brake_force_kn(value):
    """
    Стандартная неопределенность тормозной силы на стенде.

    Относительная погрешность ±3%.
    Значение тормозной силы хранится в кН.
    """
    return standard_brake_force_kn(value)


def standard_brake_force_kn(value):
    """Standard uncertainty of a brake force including 10 N resolution."""
    value = decimal_value(value)
    if value is None:
        return None

    relative = standard_uncertainty_from_relative_error(value, Decimal("3"))
    resolution = Decimal("0.01") / (Decimal("2") * SQRT_3)
    return root_sum_squares(relative, resolution)


def u_stand_load_standard_kg(value):
    """
    Стандартная неопределенность нагрузки на ось стенда.

    Погрешность стенда по нагрузке ±3%.
    """
    return standard_stand_load_kg(value)


def standard_stand_load_kg(value):
    """Standard uncertainty of a stand load including 1 kg resolution."""
    value = decimal_value(value)
    if value is None:
        return None

    relative = standard_uncertainty_from_relative_error(value, Decimal("3"))
    resolution = Decimal("1") / (Decimal("2") * SQRT_3)
    return root_sum_squares(relative, resolution)


def u_control_force_n(value):
    """
    Усилие на органе управления тормозной системой.

    Excel:
    ΔF = δ × F
    δ = 5%

    uB(F) = ΔF / sqrt(3) = δ × F / sqrt(3)
    U = k × uB(F)

    Пример:
    F = 98 Н
    uB = 98 × 0.05 / sqrt(3) = 2.83 Н
    U = 1.65 × 2.83 = 4.67 Н
    """
    value = decimal_value(value)
    if value is None:
        return None

    relative = standard_uncertainty_from_relative_error(value, Decimal("5"))
    resolution = Decimal("1") / (Decimal("2") * SQRT_3)

    return expanded_from_standard(root_sum_squares(relative, resolution))


def calc_service_brake_specific_force_uncertainty(brake, measurement):
    """
    Неопределенность удельной тормозной силы рабочей тормозной системы.

    Excel:
    R = (P1 + P2 + P3 + P4) / (m * g)

    где:
    P1..P4 — тормозные силы, Н
    m — масса, кг
    g = 9.800

    u(R) = sqrt(
        (1 / (m * g))^2 * (u^2(P1) + u^2(P2) + u^2(P3) + u^2(P4))
        +
        ((P1 + P2 + P3 + P4) / (m^2 * g))^2 * u^2(m)
    )

    U = 1.65 * u(R)

    Массу берем так же, как в расчете:
    1) axle1_load_kg + axle2_load_kg;
    2) если нагрузок на оси нет — vehicle_weight_kg.
    """
    forces_kn = [
        decimal_value(get_value(brake, "service_brake_front_left_kn")),
        decimal_value(get_value(brake, "service_brake_front_right_kn")),
        decimal_value(get_value(brake, "service_brake_rear_left_kn")),
        decimal_value(get_value(brake, "service_brake_rear_right_kn")),
    ]

    forces_kn = [value for value in forces_kn if value is not None]

    mass_kg = get_vehicle_mass_for_brake_calc(measurement)

    if not forces_kn or mass_kg is None or mass_kg == 0:
        return None

    forces_n = [value * Decimal("1000") for value in forces_kn]
    force_sum_n = sum(forces_n)

    u_forces_squared_sum = sum(
        (standard_brake_force_kn(force_n / Decimal("1000")) * Decimal("1000")) ** 2
        for force_n in forces_n
    )

    u_mass = standard_stand_load_kg(mass_kg)

    if u_mass is None:
        return None

    coefficient_force = (Decimal("1") / (mass_kg * G)) ** 2
    coefficient_mass = (force_sum_n / (mass_kg * mass_kg * G)) ** 2

    standard_u = (
        coefficient_force * u_forces_squared_sum
        +
        coefficient_mass * (u_mass ** 2)
    ).sqrt()

    return expanded_from_standard(standard_u)


def calc_parking_brake_specific_force_uncertainty(brake, measurement):
    """
    Неопределенность удельной тормозной силы стояночной тормозной системы.

    R = (P_left + P_right) / (m * g)

    Массу берем так же, как в расчете:
    1) axle1_load_kg + axle2_load_kg;
    2) если нагрузок на оси нет — vehicle_weight_kg.
    """
    forces_kn = [
        decimal_value(get_value(brake, "parking_brake_left_kn")),
        decimal_value(get_value(brake, "parking_brake_right_kn")),
    ]

    forces_kn = [value for value in forces_kn if value is not None]

    mass_kg = get_vehicle_mass_for_brake_calc(measurement)

    if not forces_kn or mass_kg is None or mass_kg == 0:
        return None

    forces_n = [value * Decimal("1000") for value in forces_kn]
    force_sum_n = sum(forces_n)

    u_forces_squared_sum = sum(
        (standard_brake_force_kn(force_n / Decimal("1000")) * Decimal("1000")) ** 2
        for force_n in forces_n
    )

    u_mass = standard_stand_load_kg(mass_kg)

    if u_mass is None:
        return None

    coefficient_force = (Decimal("1") / (mass_kg * G)) ** 2
    coefficient_mass = (force_sum_n / (mass_kg * mass_kg * G)) ** 2

    standard_u = (
        coefficient_force * u_forces_squared_sum
        +
        coefficient_mass * (u_mass ** 2)
    ).sqrt()

    return expanded_from_standard(standard_u)


def brake_difference_pct(left_force, right_force):
    """
    Относительная разность тормозных сил колес оси.

    Главное правило:
    D = 100 * (max - min) / max

    где:
    max — большее значение тормозной силы на оси;
    min — меньшее значение тормозной силы на оси.
    """
    left = decimal_value(left_force)
    right = decimal_value(right_force)

    if left is None or right is None:
        return None

    p_max = max(left, right)
    p_min = min(left, right)

    if p_max == 0:
        return None

    return Decimal("100") * (p_max - p_min) / p_max


def calc_brake_difference_uncertainty(left_force, right_force):
    """
    Расширенная неопределенность относительной разности тормозных сил колес оси.

    Формула самой разности:
    D = 100 * (Pmax - Pmin) / Pmax

    где:
    Pmax — большее значение тормозной силы на оси;
    Pmin — меньшее значение тормозной силы на оси.

    В форме и БД тормозные силы хранятся в кН.
    В расчете неопределенности переводим:
    кН -> Н

    D = 100 * (1 - Pmin / Pmax)

    Частные производные:
    dD/dPmin = -100 / Pmax
    dD/dPmax = 100 * Pmin / Pmax^2

    u(D) = sqrt(
        (-100 / Pmax)^2 * u(Pmin)^2
        +
        (100 * Pmin / Pmax^2)^2 * u(Pmax)^2
    )

    U = 1.65 * u(D)
    """
    left_kn = decimal_value(left_force)
    right_kn = decimal_value(right_force)

    if left_kn is None or right_kn is None:
        return None

    left_n = left_kn * Decimal("1000")
    right_n = right_kn * Decimal("1000")

    p_max = max(left_n, right_n)
    p_min = min(left_n, right_n)

    if p_max == 0:
        return None

    u_p_max = standard_brake_force_kn(p_max / Decimal("1000")) * Decimal("1000")
    u_p_min = standard_brake_force_kn(p_min / Decimal("1000")) * Decimal("1000")

    if u_p_max is None or u_p_min is None:
        return None

    coefficient_p_min = Decimal("100") / p_max
    coefficient_p_max = Decimal("100") * p_min / (p_max * p_max)

    standard_u = root_sum_squares(
        coefficient_p_min * u_p_min,
        coefficient_p_max * u_p_max,
    )

    return expanded_from_standard(standard_u)


def calc_axle_1_brake_difference_uncertainty(brake):
    return calc_brake_difference_uncertainty(
        get_value(brake, "service_brake_front_left_kn"),
        get_value(brake, "service_brake_front_right_kn"),
    )


def calc_axle_2_brake_difference_uncertainty(brake):
    return calc_brake_difference_uncertainty(
        get_value(brake, "service_brake_rear_left_kn"),
        get_value(brake, "service_brake_rear_right_kn"),
    )


# =========================
# Сила света
# =========================

def standard_headlight_uncertainty_cd(value):
    """Standard uncertainty for headlight intensity from the new workbook."""
    value = decimal_value(value)

    if value is None:
        return None

    relative = standard_uncertainty_from_relative_error(value, Decimal("15"))
    resolution = Decimal("0.1") / (Decimal("2") * SQRT_3)

    return root_sum_squares(relative, resolution)


def u_headlight_cd(value):
    """
    Сила света фар.

    Excel:
    Относительная погрешность измерителя параметров света фар ИПФ-1 = ±15%.
    Дополнительно учитывается цена деления 0,1 кд.

    u = value * 15 / 100 / sqrt(3)
    U = 1.65 * u

    Пример:
    450 кд -> 450 * 0.15 / sqrt(3) * 1.65 = 64.30 кд
    """
    return expanded_from_standard(standard_headlight_uncertainty_cd(value))


def u_total_high_beam_cd(light):
    """
    Неопределенность максимальной силы света всех фар дальнего света.

    Excel:
    u_left = sqrt((left_high_beam_cd * 15 / 100 / sqrt(3))^2 + (0.1 / (2 * sqrt(3)))^2)
    u_right = sqrt((right_high_beam_cd * 15 / 100 / sqrt(3))^2 + (0.1 / (2 * sqrt(3)))^2)

    u_total = sqrt(u_left^2 + u_right^2)
    U_total = 1.65 * u_total
    """
    left = decimal_value(get_value(light, "left_high_beam_cd"))
    right = decimal_value(get_value(light, "right_high_beam_cd"))

    if left is None and right is None:
        return None

    standard_values = []

    if left is not None:
        standard_values.append(standard_headlight_uncertainty_cd(left))

    if right is not None:
        standard_values.append(standard_headlight_uncertainty_cd(right))

    standard_u = root_sum_squares(*standard_values)

    return expanded_from_standard(standard_u)


# =========================
# Главная сборка неопределенностей
# =========================

def build_uncertainty_values(protocol=None):
    measurement = get_related_safe(protocol, "measurement") if protocol else None
    brake = get_related_safe(protocol, "brake") if protocol else None
    light = get_related_safe(protocol, "light") if protocol else None

    co_u = u_co_pct()
    noise_u = u_noise_db()
    steering_u = u_steering_backlash_deg()
    linear_02_u = u_linear_02_mm()
    bumper_distance_u = u_bumper_distance_mm()
    protruding_elements_u = u_protruding_elements_mm()
    tire_depth_u = u_tire_depth_mm()
    glass_u = u_glass_transparency_pct()

    speed_by_speedometer_u = u_speed_kmh(
        get_value(measurement, "speed_by_speedometer_kmh")
    )

    actual_speed_u = u_speed_kmh(
        get_value(measurement, "actual_speed_kmh")
    )

    turn_hz_u = u_turn_signal_frequency_hz()
    turn_per_min_u = u_turn_signal_frequency_per_min()
    light_absorption_u = calc_light_absorption_uncertainty(measurement)

    length_u_mm = u_vehicle_length_mm(
        get_value(measurement, "vehicle_length_mm")
    )

    width_u_mm = u_vehicle_width_mm(
        get_value(measurement, "vehicle_width_mm")
    )

    height_u_mm = u_vehicle_height_mm(
        get_value(measurement, "vehicle_height_mm")
    )

    scale_u = u_scale_kg()

    stand_axle1_u = u_stand_load_kg(
        get_value(measurement, "stand_axle1_load_kg")
    )
    stand_axle2_u = u_stand_load_kg(
        get_value(measurement, "stand_axle2_load_kg")
    )

    service_control_force_axle1_u = u_control_force_n(
        get_value(brake, "service_brake_control_force_axle1_n")
    )

    service_control_force_axle2_u = u_control_force_n(
        get_value(brake, "service_brake_control_force_axle2_n")
    )

    parking_control_force_u = u_control_force_n(
        get_value(brake, "parking_brake_control_force_n")
    )

    service_specific_u = calc_service_brake_specific_force_uncertainty(
        brake,
        measurement,
    )

    parking_specific_u = calc_parking_brake_specific_force_uncertainty(
        brake,
        measurement,
    )

    axle_1_difference_u = calc_axle_1_brake_difference_uncertainty(brake)
    axle_2_difference_u = calc_axle_2_brake_difference_uncertainty(brake)

    left_34v_u = u_headlight_cd(get_value(light, "left_34v_cd"))
    left_52h_u = u_headlight_cd(get_value(light, "left_52h_cd"))
    left_high_beam_u = u_headlight_cd(get_value(light, "left_high_beam_cd"))

    right_34v_u = u_headlight_cd(get_value(light, "right_34v_cd"))
    right_52h_u = u_headlight_cd(get_value(light, "right_52h_cd"))
    right_high_beam_u = u_headlight_cd(get_value(light, "right_high_beam_cd"))

    total_high_beam_u = u_total_high_beam_cd(light)

    return {
        # =========================
        # CO
        # =========================
        "u_co_min_pct": fmt_num(co_u, 2),
        "u_co_max_pct": fmt_num(co_u, 2),

        # =========================
        # Шум
        # =========================
        "u_exhaust_noise_constant_db": fmt_num(noise_u, 2),
        "u_exhaust_noise_deceleration_db": fmt_num(noise_u, 2),

        # =========================
        # Рулевое управление
        # =========================
        "u_steering_backlash_deg": fmt_num(steering_u, 2),

        # =========================
        # Габариты в мм
        # =========================
        "u_vehicle_length_mm": fmt_num(length_u_mm, 1),
        "u_vehicle_width_mm": fmt_num(width_u_mm, 1),
        "u_vehicle_height_mm": fmt_num(height_u_mm, 1),

        # =========================
        # Масса и оси по весам
        # =========================
        "u_vehicle_weight_kg": fmt_num(scale_u, 0),
        "u_axle1_load_kg": fmt_num(scale_u, 0),
        "u_axle2_load_kg": fmt_num(scale_u, 0),

        # =========================
        # Нагрузка на оси на тормозном стенде
        # =========================
        "u_stand_axle1_load_kg": fmt_num(stand_axle1_u, 2),
        "u_stand_axle2_load_kg": fmt_num(stand_axle2_u, 2),

        # =========================
        # Тормоза
        # =========================
        "u_service_brake_control_force_axle1_n": fmt_num(service_control_force_axle1_u, 2),
        "u_service_brake_control_force_axle2_n": fmt_num(service_control_force_axle2_u, 2),
        "u_parking_brake_control_force_n": fmt_num(parking_control_force_u, 2),

        "u_service_brake_specific_force": fmt_num(service_specific_u, 2),
        "u_parking_brake_specific_force": fmt_num(parking_specific_u, 2),

        "u_axle_1_brake_difference_pct": fmt_num(axle_1_difference_u, 2),
        "u_axle_2_brake_difference_pct": fmt_num(axle_2_difference_u, 2),

        # =========================
        # Геометрия света
        # Автоподбор Δ:
        # 0–9 мм -> 0.15
        # 10–99 мм -> 0.20
        # 100–5000 мм -> 0.30
        # =========================
        "u_low_beam_lower_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "low_beam_lower_point_mm")),
            2,
        ),
        "u_low_beam_upper_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "low_beam_upper_point_mm")),
            2,
        ),

        "u_fog_light_left_distance_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "fog_light_left_distance_mm")),
            2,
        ),
        "u_fog_light_right_distance_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "fog_light_right_distance_mm")),
            2,
        ),
        "u_fog_light_lower_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "fog_light_lower_point_mm")),
            2,
        ),
        "u_fog_light_upper_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "fog_light_upper_point_mm")),
            2,
        ),

        "u_brake_signal_left_distance_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "brake_signal_left_distance_mm")),
            2,
        ),
        "u_brake_signal_right_distance_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "brake_signal_right_distance_mm")),
            2,
        ),
        "u_brake_signal_lower_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "brake_signal_lower_point_mm")),
            2,
        ),
        "u_brake_signal_upper_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "brake_signal_upper_point_mm")),
            2,
        ),

        "u_additional_brake_signal_from_support_surface_mm": fmt_num(
            u_linear_by_value_mm(
                get_value(light, "additional_brake_signal_from_support_surface_mm")
            ),
            2,
        ),
        "u_additional_brake_signal_from_glass_edge_mm": fmt_num(
            u_linear_by_value_mm(
                get_value(light, "additional_brake_signal_from_glass_edge_mm")
            ),
            2,
        ),
        "u_additional_brake_signal_optical_center_shift_mm": fmt_num(
            u_linear_by_value_mm(
                get_value(light, "additional_brake_signal_optical_center_shift_mm")
            ),
            2,
        ),

        "u_rear_fog_upper_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "rear_fog_upper_point_mm")),
            2,
        ),
        "u_rear_fog_lower_point_mm": fmt_num(
            u_linear_by_value_mm(get_value(light, "rear_fog_lower_point_mm")),
            2,
        ),

        # =========================
        # Сила света
        # =========================
        "u_left_34v_cd": fmt_num(left_34v_u, 2),
        "u_left_52h_cd": fmt_num(left_52h_u, 2),
        "u_left_high_beam_cd": fmt_num(left_high_beam_u, 2),

        "u_right_34v_cd": fmt_num(right_34v_u, 2),
        "u_right_52h_cd": fmt_num(right_52h_u, 2),
        "u_right_high_beam_cd": fmt_num(right_high_beam_u, 2),

        "u_calc_total_high_beam_cd": fmt_num(total_high_beam_u, 2),

        # =========================
        # Частота указателей
        # =========================
        "u_turn_signal_frequency_hz": fmt_num(turn_hz_u, 1),
        "u_turn_signal_frequency_per_min": fmt_num(turn_per_min_u, 0),

        # =========================
        # Шины
        # =========================
        "u_tire_depth_fl_mm": fmt_num(tire_depth_u, 2),
        "u_tire_depth_fr_mm": fmt_num(tire_depth_u, 2),
        "u_tire_depth_rl_mm": fmt_num(tire_depth_u, 2),
        "u_tire_depth_rr_mm": fmt_num(tire_depth_u, 2),

        # =========================
        # Стекла
        # =========================
        "u_glass_transparency_windshield_pct": fmt_num(glass_u, 1),
        "u_glass_transparency_right_pct": fmt_num(glass_u, 1),
        "u_glass_transparency_left_pct": fmt_num(glass_u, 1),

        # =========================
        # Дымность / коэффициент поглощения света
        # =========================
        "u_calc_light_absorption_average": fmt_num(light_absorption_u, 2),

        # =========================
        # Прочее
        # =========================
        "u_sun_strip_width_mm": fmt_num(linear_02_u, 2),
        "u_bumper_to_body_distance_mm": fmt_num(bumper_distance_u, 2),
        "u_protruding_elements_doors_mm": fmt_num(protruding_elements_u, 2),
        "u_protruding_elements_other_mm": fmt_num(protruding_elements_u, 2),

        "u_speed_by_speedometer_kmh": fmt_num(speed_by_speedometer_u, 2),
        "u_actual_speed_kmh": fmt_num(actual_speed_u, 2),
    }