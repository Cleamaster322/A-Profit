"""
Лист оценки неопределенности к протоколу (Excel).

Строки листа — по прототипу «Лист оценки» из templates/29.10.26/Расчет_неопределенност28.10.26.xlsx.
Для каждой строки считаются X (результат), uA, uB, uc и U = 1,65·uc теми же функциями,
что и неопределенности в протоколе (protocol_docx/calculations.py), поэтому числа совпадают.

В контекст шаблона идут ключи ev_<код>_x / _n / _ua / _ub / _uc / _u / _error,
а также условия строк ev_*_present и т. п. (см. EVALUATION_CONDITIONS).
Строки ГРЗ из прототипа не выводятся — в работе ГРЗ не будет.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Optional

from .protocol_docx.calculations import (
    K_95,
    SQRT_3,
    brake_difference_pct,
    calc_axle_1_brake_difference_uncertainty,
    calc_axle_2_brake_difference_uncertainty,
    calc_light_absorption_average,
    calc_parking_brake_specific_force,
    calc_parking_brake_specific_force_uncertainty,
    calc_service_brake_specific_force,
    calc_service_brake_specific_force_uncertainty,
    calc_total_high_beam_cd,
    get_related_safe,
    get_value,
    linear_abs_error_by_value_mm,
    rgk_r5_vehicle_abs_error_mm,
    root_sum_squares,
    standard_headlight_uncertainty_cd,
    standard_stand_load_kg,
    standard_uncertainty_from_abs_error,
    standard_uncertainty_from_relative_error,
    standard_uncertainty_type_a,
    u_total_high_beam_cd,
)
from .protocol_docx.formatters import decimal_value, fmt_date, fmt_text

# =========================
# Средства измерения (текст колонки «Оборудование»)
# =========================

STAND = "Стенд тормозной СТН 13000.01\nЗав. № 507\nИнв. № СИ006"
TAPE = "Рулетка RGK R-5\nЗав. № 2438\nИнв. № СИ035"
IPF = "Измеритель параметров света фар автотранспортных средств ИПФ-01\nЗав. № 9843\nИнв. № СИ001"
CALIPER = "Штангенциркуль ШЦ-I-150-0,05\nЗав. № Н321080361\nИнв. № СИ008"
TONIK = "Измеритель светопропускания стекол «ТОНИК»\nЗав. № 18861\nИнв. № СИ004"
ISD = "Измеритель скорости и длины ИСД-5.1\nЗав. № 2024.5379\nИнв. № СИ013"
RULER = "Линейка измерительная металлическая L300\nЗав. № 99\nИнв. № СИ023"
GAS_ANALYZER = "Газоанализатор многокомпонентный «АВТОТЕСТ-02.02»\nЗав. № 26403\nИнв. № СИ005"
SMOKE_METER = "Дымомер АВГ-1Д-4.01\nЗав. № 33\nИнв. № СИ003"
NOISE_METER = (
    "Шумомер-анализатор спектра портативный ОКТАВА-111 + Микрофонный предусилитель Р200\n"
    "Зав. № 248268\nИнв. № СИ014"
)
ISL = "Преобразователь измерительный угла поворота ИСЛ-М\nЗав. № 19694\nИнв. № СИ002"
LASER = "Дальномер лазерный RGK DL50\nЗав. № 23F001640\nИнв. № СИ033"

GOST_33670 = "Приложения А, ГОСТ 33670-2015"


@dataclass(frozen=True)
class EvaluationRow:
    key: str
    method: str
    characteristic: str
    units: str
    equipment: str
    error: str
    compute: Callable
    # Ключ условия из EVALUATION_CONDITIONS; None — строка выводится всегда.
    condition: Optional[str] = None


@dataclass
class RowResult:
    x: Optional[Decimal]
    ua: Optional[Decimal]
    ub: Optional[Decimal]
    uc: Optional[Decimal]
    count: int = 1
    error: Optional[str] = None

    @property
    def u(self):
        return None if self.uc is None else K_95 * self.uc


def resolution_u(step):
    """Неопределенность от цены деления: d / (2·√3)."""
    return Decimal(str(step)) / (Decimal("2") * SQRT_3)


def single(value, ub, error=None):
    """Одно измерение: uA = 0, uc = uB."""
    x = decimal_value(value)
    if x is None or ub is None:
        return RowResult(x, None, None, None, error=error)
    return RowResult(x, Decimal("0"), ub, ub, error=error)


def derived(x, expanded):
    """Косвенная величина: uB отдельно не считается («-»), uc = U / 1,65."""
    x = decimal_value(x)
    if x is None or expanded is None:
        return RowResult(x, None, None, None)
    return RowResult(x, Decimal("0"), None, expanded / K_95)


def format_error_mm(delta):
    return f"±{str(delta.normalize()).replace('.', ',')} мм" if delta is not None else "-"


# =========================
# Расчет строк
# =========================

def abs_error_row(field, section, delta, resolution=None):
    def compute(sections):
        value = get_value(sections[section], field)
        ub = standard_uncertainty_from_abs_error(Decimal(delta))
        if resolution is not None:
            ub = root_sum_squares(ub, resolution_u(resolution))
        return single(value, ub)
    return compute


def relative_error_row(field, section, percent, resolution=None):
    def compute(sections):
        value = get_value(sections[section], field)
        ub = standard_uncertainty_from_relative_error(value, Decimal(percent))
        if ub is not None and resolution is not None:
            ub = root_sum_squares(ub, resolution_u(resolution))
        return single(value, ub)
    return compute


def linear_by_value_row(field, section="light"):
    """Геометрия световых приборов: Δ рулетки подбирается по значению (0,15 / 0,2 / 0,3 мм)."""
    def compute(sections):
        value = get_value(sections[section], field)
        delta = linear_abs_error_by_value_mm(value)
        ub = standard_uncertainty_from_abs_error(delta) if delta is not None else None
        return single(value, ub, error=format_error_mm(delta))
    return compute


def vehicle_size_row(field):
    """Длина / ширина: Δ = 0,3 + 0,15·(N − 1) мм, N — метровый интервал."""
    def compute(sections):
        value = get_value(sections["measurement"], field)
        delta = rgk_r5_vehicle_abs_error_mm(value)
        ub = standard_uncertainty_from_abs_error(delta) if delta is not None else None
        return single(value, ub, error=format_error_mm(delta))
    return compute


def control_force_row(field):
    return relative_error_row(field, "brake", "5", resolution=1)


def headlight_row(field):
    def compute(sections):
        value = get_value(sections["light"], field)
        return single(value, standard_headlight_uncertainty_cd(value))
    return compute


def axle_load_row(field):
    def compute(sections):
        value = get_value(sections["measurement"], field)
        return single(value, standard_stand_load_kg(value))
    return compute


def brake_difference_row(axle):
    def compute(sections):
        brake = sections["brake"]
        stored = get_value(brake, f"axle_{axle}_brake_difference_pct")
        if axle == 1:
            left, right = "service_brake_front_left_kn", "service_brake_front_right_kn"
            expanded = calc_axle_1_brake_difference_uncertainty(brake)
        else:
            left, right = "service_brake_rear_left_kn", "service_brake_rear_right_kn"
            expanded = calc_axle_2_brake_difference_uncertainty(brake)
        x = stored if stored is not None else brake_difference_pct(get_value(brake, left), get_value(brake, right))
        return derived(x, expanded)
    return compute


def specific_force_service(sections):
    return derived(
        calc_service_brake_specific_force(sections["brake"], sections["measurement"]),
        calc_service_brake_specific_force_uncertainty(sections["brake"], sections["measurement"]),
    )


def specific_force_parking(sections):
    return derived(
        calc_parking_brake_specific_force(sections["brake"], sections["measurement"]),
        calc_parking_brake_specific_force_uncertainty(sections["brake"], sections["measurement"]),
    )


def total_high_beam(sections):
    return derived(calc_total_high_beam_cd(sections["light"]), u_total_high_beam_cd(sections["light"]))


def turn_signal_per_min(sections):
    hz = abs_error_row("turn_signal_frequency_hz", "light", "0.1", resolution="0.1")(sections)
    if hz.x is None:
        return hz
    sixty = Decimal("60")
    return RowResult(hz.x * sixty, Decimal("0"), hz.ub * sixty, hz.uc * sixty)


def light_absorption(sections):
    """Дымность: 6 замеров — uA по типу А, uB = √((0,05/√3)² + (0,001/(2√3))²)."""
    measurement = sections["measurement"]
    values = [get_value(measurement, f"light_absorption_{index}") for index in range(1, 7)]
    present = [value for value in values if value is not None]
    x = calc_light_absorption_average(measurement)
    ub = root_sum_squares(standard_uncertainty_from_abs_error(Decimal("0.05")), resolution_u("0.001"))
    if x is None:
        return RowResult(None, None, None, None, count=len(present))
    ua = standard_uncertainty_type_a(values) or Decimal("0")
    return RowResult(x, ua, ub, root_sum_squares(ua, ub), count=len(present))


def copy_of(key):
    """Та же величина по другому ГОСТ (ГОСТ 33987) — значения берутся из строки key."""
    def compute(sections):
        return sections["_results"][key]
    return compute


def _rows():
    rows = []

    def add(key, method, characteristic, units, equipment, error, compute, condition=None):
        rows.append(EvaluationRow(key, method, characteristic, units, equipment, error, compute, condition))

    # Тормоза
    add("service_control_force_axle1", f"п.А.5.1.1.3 {GOST_33670}",
        "Усилие на органе управления рабочей тормозной системы 1 Оси", "Ньютон, Н", STAND,
        "Относительная ± 5%", control_force_row("service_brake_control_force_axle1_n"))
    add("service_control_force_axle2", f"п.А.5.1.1.3 {GOST_33670}",
        "Усилие на органе управления рабочей тормозной системы 2 Оси", "Ньютон, Н", STAND,
        "Относительная ± 5%", control_force_row("service_brake_control_force_axle2_n"))
    add("parking_control_force", f"п.А.5.1.5 {GOST_33670}",
        "Усилие на органе управления стояночной тормозной системы", "Ньютон, Н", STAND,
        "Относительная ± 5%", control_force_row("parking_brake_control_force_n"),
        condition="ev_parking_control_force_applicable")
    add("brake_difference_axle1", f"п.А.5.1.1.4, А.5.9 {GOST_33670}",
        "Относительная разность тормозных сил колес 1 оси", "Проценты, %", STAND,
        "Относительная ± 3%", brake_difference_row(1))
    add("brake_difference_axle2", f"п.А.5.1.1.4, А.5.9 {GOST_33670}",
        "Относительная разность тормозных сил колес 2 оси", "Проценты, %", STAND,
        "Относительная ± 3%", brake_difference_row(2))
    add("service_specific_force", f"п.А.5.1.1.3, п.А.5.9 {GOST_33670}",
        "Удельная тормозная сила рабочей тормозной системы", "Безразмерная величина", STAND,
        "Относительная ± 3%", specific_force_service)
    add("parking_specific_force", f"п.А.5.1.4.1.1, п.А.5.9 {GOST_33670}",
        "Удельная тормозная сила стояночной тормозной системы", "Безразмерная величина", STAND,
        "Относительная ± 3%", specific_force_parking)
    add("axle1_load", f"п.А.5 {GOST_33670}", "Нагрузка на 1 ось", "Килограммы, кг", STAND,
        "Относительная ± 3%", axle_load_row("axle1_load_kg"))
    add("axle2_load", f"п.А.5 {GOST_33670}", "Нагрузка на 2 ось", "Килограммы, кг", STAND,
        "Относительная ± 3%", axle_load_row("axle2_load_kg"))

    # Фары ближнего света: левая и правая меряются одной парой полей.
    for side, side_name in (("left", "левой"), ("right", "правой")):
        add(f"low_beam_lower_{side}", f"п.А.8.9 {GOST_33670}",
            f"Высота нижней границы размещения {side_name} фары ближнего света над опорной поверхностью",
            "миллиметры, мм", TAPE, "", linear_by_value_row("low_beam_lower_point_mm"))
    for side, side_name in (("left", "левой"), ("right", "правой")):
        add(f"low_beam_upper_{side}", f"п.А.8.9 {GOST_33670}",
            f"Высота верхней границы размещения {side_name} фары ближнего света над опорной поверхностью",
            "миллиметры, мм", TAPE, "", linear_by_value_row("low_beam_upper_point_mm"))

    # Передние ПТФ
    add("front_fog_width_left", "п. А.8.10.1 Приложения А ГОСТ 33670-2015",
        "Расстояние от наиболее удаленной от средней продольной плоскости точки видимой поверхности "
        "передней левой противотуманной фары до края габаритной ширины ТС",
        "миллиметры, мм", TAPE, "", linear_by_value_row("fog_light_left_distance_mm"), "ev_front_fog_present")
    add("front_fog_width_right", "п. А.8.10.1 Приложения А ГОСТ 33670-2015",
        "Расстояние от наиболее удаленной от средней продольной плоскости точки видимой поверхности "
        "передней правой противотуманной фары до края габаритной ширины ТС",
        "миллиметры, мм", TAPE, "", linear_by_value_row("fog_light_right_distance_mm"), "ev_front_fog_present")
    for point, point_name in (("lower", "нижней"), ("upper", "верхней")):
        for side, side_name in (("left", "левой"), ("right", "правой")):
            add(f"front_fog_{point}_{side}", "п. А.8.10.2 Приложения А ГОСТ 33670-2015",
                f"Расстояние от {point_name} точки {side_name} передней противотуманной фары до опорной поверхности",
                "миллиметры, мм", TAPE, "", linear_by_value_row(f"fog_light_{point}_point_mm"), "ev_front_fog_present")

    # Сигналы торможения
    for side, side_name in (("left", "левого"), ("right", "правого")):
        add(f"brake_signal_width_{side}", f"п.А.8.12.1 {GOST_33670}",
            f"Расстояние от наиболее удаленной от средней продольной плоскости точки видимой поверхности "
            f"{side_name} сигнала торможения до края габаритной ширины ТС",
            "миллиметры, мм", TAPE, "", linear_by_value_row(f"brake_signal_{side}_distance_mm"))
    for point, point_name in (("lower", "нижней"), ("upper", "верхней")):
        for side, side_name in (("left", "левого"), ("right", "правого")):
            add(f"brake_signal_{point}_{side}", f"п.А.8.12.2 {GOST_33670}",
                f"Расстояние от {point_name} точки {side_name} сигнала торможения на кузове до опорной поверхности",
                "миллиметры, мм", TAPE, "", linear_by_value_row(f"brake_signal_{point}_point_mm"))
    add("additional_brake_support", f"п.А.8.12.3 {GOST_33670}",
        "Расстояние от дополнительного сигнала торможения до опорной поверхности",
        "миллиметры, мм", TAPE, "", linear_by_value_row("additional_brake_signal_from_support_surface_mm"))
    add("additional_brake_glass_edge", f"п.А.8.12.3 {GOST_33670}",
        "Расстояние от дополнительного сигнала торможения до нижнего края внешней поверхности "
        "или покрытия заднего стекла",
        "миллиметры, мм", TAPE, "", linear_by_value_row("additional_brake_signal_from_glass_edge_mm"))
    add("additional_brake_center_shift", f"п.А.8.12.4 {GOST_33670}",
        "Смещение оптического центра дополнительного сигнала торможения влево или вправо "
        "от оси симметрии транспортного средства",
        "миллиметры, мм", TAPE, "", linear_by_value_row("additional_brake_signal_optical_center_shift_mm"))

    # Задние ПТФ: при двух фонарях правый повторяет значения левого.
    for point, point_name in (("lower", "нижней"), ("upper", "верхней")):
        add(f"rear_fog_{point}_left", f"п.А.8.13.2 {GOST_33670}",
            f"Расстояние от {point_name} точки левого заднего противотуманного фонаря до опорной поверхности",
            "миллиметры, мм", TAPE, "", linear_by_value_row(f"rear_fog_{point}_point_mm"), "ev_rear_fog_present")
        add(f"rear_fog_{point}_right", f"п.А.8.13.2 {GOST_33670}",
            f"Расстояние от {point_name} точки правого заднего противотуманного фонаря до опорной поверхности",
            "миллиметры, мм", TAPE, "", linear_by_value_row(f"rear_fog_{point}_point_mm"), "ev_rear_fog_two_lamps")

    # Сила света
    for field, direction in (("34v", "34' вверх"), ("52h", "52' вниз")):
        for side, side_name in (("left", "левой"), ("right", "правой")):
            add(f"headlight_{field}_{side}", f"п.А.8.20.6 {GOST_33670}",
                f"Сила света {side_name} фары в направлении {direction} от положения левой части светотеневой границы",
                "Канделы, кд", IPF, "± 15%", headlight_row(f"{side}_{field}_cd"))
    for side, side_name in (("left", "левой"), ("right", "правой")):
        add(f"high_beam_{side}", f"п.А.8.20.7 {GOST_33670}",
            f'Максимальная сила света {side_name} фары в режиме "Дальний свет"',
            "Канделы, кд", IPF, "± 15%", headlight_row(f"{side}_high_beam_cd"))
    add("high_beam_total", f"п.А.8.20.7 {GOST_33670}",
        'Максимальная сила света всех фар в режиме "Дальний свет"', "Канделы, кд", IPF, "± 15%", total_high_beam)

    # Указатели поворота и аварийная сигнализация (одна и та же частота)
    turn_hz = abs_error_row("turn_signal_frequency_hz", "light", "0.1", resolution="0.1")
    add("turn_signal_hz", f"п.А.8.22.1 {GOST_33670}", "Частота следования проблесков указателей поворота",
        "Герц, Гц", IPF, "± 0,1 Гц", turn_hz)
    add("turn_signal_per_min", f"п.А.8.22.1 {GOST_33670}", "Частота следования проблесков указателей поворота",
        "(проблесков в минуту)", IPF, "± 0,1 Гц", turn_signal_per_min)
    add("hazard_hz", f"п.А.8.22.2 {GOST_33670}", "Частота следования проблесков аварийной сигнализации",
        "Герц, Гц", IPF, "± 0,1 Гц", turn_hz)
    add("hazard_per_min", f"п.А.8.22.2 {GOST_33670}", "Частота следования проблесков аварийной сигнализации",
        "(проблесков в минуту)", IPF, "± 0,1 Гц", turn_signal_per_min)

    # Протектор: А.10.7.2 всегда, А.10.7.3 — только для зимних шин.
    tires = (("fl", "передней левой"), ("fr", "передней правой"), ("rl", "задней левой"), ("rr", "задней правой"))
    for clause, condition in (("10.7.2", None), ("10.7.3", "ev_winter_tires")):
        for tire, tire_name in tires:
            add(f"tire_depth_{clause.replace('.', '_')}_{tire}", f"п.А.{clause} {GOST_33670}",
                f"Остаточная глубина рисунка протектора {tire_name} шины", "Миллиметры, мм", CALIPER,
                "± 0,05 мм", abs_error_row(f"tire_depth_{tire}_mm", "measurement", "0.05"), condition)

    # Стекла, полоса, скорость, бампер, выступы
    for field, name in (("windshield", "ветрового"), ("right", "правого"), ("left", "левого")):
        add(f"glass_{field}", f"п.А.11.8 {GOST_33670}", f"Светопропускание {name} стекла", "Проценты, %",
            TONIK, "± 2 %", abs_error_row(f"glass_transparency_{field}_pct", "measurement", "2", resolution="0.1"))
    add("sun_strip", f"п.А.11.8 {GOST_33670}", "Ширина светозащитной полосы", "Миллиметры, мм", TAPE,
        "± 0,2 мм", abs_error_row("sun_strip_width_mm", "measurement", "0.2"), "ev_sun_strip_present")
    add("speed", f"п.А.12.3 {GOST_33670}", "Скорость транспортного средства", "Километры в час, км/ч", ISD,
        "± 0,15 %", relative_error_row("speed_by_speedometer_kmh", "measurement", "0.15", resolution="0.1"))
    add("bumper_distance", f"п.А.16.7 {GOST_33670}", "Расстояние между краем бампера и кузовом",
        "Миллиметры, мм", TAPE, "±0,14 мм", abs_error_row("bumper_to_body_distance_mm", "measurement", "0.14"))
    add("protrusion_doors", f"п.А.16.9 {GOST_33670}", "Выступание дверной ручки за наружную поверхность кузова",
        "Миллиметры, мм", RULER, "±0,1 мм", abs_error_row("protruding_elements_doors_mm", "measurement", "0.1"))
    add("protrusion_other", f"п.А.16.9 {GOST_33670}", "Выступающие элементы", "Миллиметры, мм", RULER,
        "±0,1 мм", abs_error_row("protruding_elements_other_mm", "measurement", "0.1"))

    # Экология: CO — бензин, дымность — дизель, шум — не для электро.
    add("co_min", f"п.А.21.7 {GOST_33670}",
        "Содержание оксида углерода (СО) в отработавших газах ТС с бензиновым двигателем в режиме "
        "холостого хода на минимальной частоте вращения коленчатого вала",
        "Процент, %", GAS_ANALYZER, "Абсолютная ± 0,03%", abs_error_row("co_min_pct", "measurement", "0.03"),
        "ev_petrol_like")
    add("co_max", f"п.А.21.7 {GOST_33670}",
        "Содержание оксида углерода (СО) в отработавших газах ТС с бензиновым двигателем на повышенной "
        "частоте вращения коленчатого вала",
        "Процент, %", GAS_ANALYZER, "Абсолютная ± 0,03%", abs_error_row("co_max_pct", "measurement", "0.03"),
        "ev_petrol_like")
    add("light_absorption", f"п.А.21.8 {GOST_33670}",
        "Дымность отработавших газов ТС с дизелями в режиме свободного ускорения",
        "натуральный показатель ослабления потока, м⁻¹", SMOKE_METER, "Абсолютная погрешность ±0,05 м⁻¹",
        light_absorption, "ev_diesel_like")
    add("noise_constant", f"п.А.23.1 {GOST_33670}",
        "Уровень шума выпуска отработавших газов ТС на холостом ходу при поддержании постоянной "
        "целевой частоты вращения",
        "Децибел А, дБА", NOISE_METER, "абсолютная ±0,5 дБА",
        abs_error_row("exhaust_noise_constant_db", "measurement", "0.5", resolution="0.1"), "ev_not_electric")
    add("noise_deceleration", f"п.А.23.1 {GOST_33670}",
        "Уровень шума выпуска отработавших газов ТС в режиме замедления от целевой частоты "
        "до минимальной частоты холостого хода",
        "Децибел А, дБА", NOISE_METER, "абсолютная ±0,5 дБА",
        abs_error_row("exhaust_noise_deceleration_db", "measurement", "0.5", resolution="0.1"), "ev_not_electric")
    add("steering_backlash", f"п.А.24.3 {GOST_33670}", "Суммарный люфт в рулевом управлении", "Градус, °", ISL,
        "±0,5 °", abs_error_row("steering_backlash_deg", "measurement", "0.5", resolution="0.1"))

    # Габариты: ГОСТ 22748 и те же значения по ГОСТ 33987.
    add("vehicle_length", "п 2.2.1, 2.2.5 ГОСТ 22748-77", "Габаритная длина транспортного средства",
        "Миллиметр, мм", TAPE, "", vehicle_size_row("vehicle_length_mm"))
    add("vehicle_width", "п 2.2.1, 2.2.2.1 ГОСТ 22748-77", "Габаритная ширина транспортного средства",
        "Миллиметр, мм", TAPE, "", vehicle_size_row("vehicle_width_mm"))
    add("vehicle_height", "п 2.2.1, 2.2.27 ГОСТ 22748-77", "Габаритная высота транспортного средства",
        "Миллиметр, мм", LASER, "±2,0 мм",
        abs_error_row("vehicle_height_mm", "measurement", "2", resolution="1"))
    add("vehicle_length_33987", "Приложение В, ГОСТ 33987-2016", "Длина транспортного средства",
        "Миллиметр, мм", TAPE, "", copy_of("vehicle_length"))
    add("vehicle_width_33987", "Приложение В, ГОСТ 33987-2016", "Ширина транспортного средства",
        "Миллиметр, мм", TAPE, "", copy_of("vehicle_width"))
    add("vehicle_height_33987", "Приложение В, ГОСТ 33987-2016", "Высота транспортного средства",
        "Миллиметр, мм", LASER, "±2,0 мм", copy_of("vehicle_height"))

    return rows


EVALUATION_ROWS = _rows()


def is_positive(value):
    number = decimal_value(value)
    return number is not None and number > 0


def evaluation_conditions(protocol, measurement, brake, light):
    fuel_type = get_value(measurement, "fuel_type")
    rear_fog_count = decimal_value(get_value(light, "rear_fog_count"))
    return {
        "ev_parking_control_force_applicable": get_value(brake, "parking_brake_type") != "electric",
        "ev_front_fog_present": is_positive(get_value(light, "front_fog_count")),
        "ev_rear_fog_present": rear_fog_count is not None and rear_fog_count > 0,
        "ev_rear_fog_two_lamps": rear_fog_count == 2,
        "ev_winter_tires": get_value(protocol, "tire_season") == "winter",
        # Как в протоколе (build_sun_strip_values): ширина 0 — полосы нет.
        "ev_sun_strip_present": is_positive(get_value(measurement, "sun_strip_width_mm")),
        "ev_petrol_like": fuel_type in {"petrol", "hybrid_petrol"},
        "ev_diesel_like": fuel_type in {"diesel", "hybrid_diesel"},
        "ev_not_electric": fuel_type != "electric",
    }


def number_or_dash(value):
    """В Excel — число (float) или «-», если величины нет."""
    return float(value) if value is not None else "-"


def build_evaluation_context(protocol):
    measurement = get_related_safe(protocol, "measurement")
    brake = get_related_safe(protocol, "brake")
    light = get_related_safe(protocol, "light")
    sections = {"measurement": measurement, "brake": brake, "light": light, "_results": {}}

    context = {
        "protocol_number": fmt_text(get_value(protocol, "protocol_number")),
        "protocol_date": fmt_date(get_value(protocol, "protocol_date")),
        **evaluation_conditions(protocol, measurement, brake, light),
    }

    for row in EVALUATION_ROWS:
        result = row.compute(sections)
        sections["_results"][row.key] = result
        prefix = f"ev_{row.key}"
        context[f"{prefix}_x"] = number_or_dash(result.x)
        context[f"{prefix}_n"] = result.count if result.x is not None else "-"
        context[f"{prefix}_ua"] = number_or_dash(result.ua)
        context[f"{prefix}_ub"] = number_or_dash(result.ub)
        context[f"{prefix}_uc"] = number_or_dash(result.uc)
        context[f"{prefix}_u"] = number_or_dash(result.u)
        context[f"{prefix}_error"] = result.error or row.error

    return context
