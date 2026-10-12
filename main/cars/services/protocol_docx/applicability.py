from .formatters import decimal_value


_EXCEL_REASON_OPTIONS = {
    "not_applicable_3_3_4": "не применяется (в конструкцию ТС не были внесены изменения до выпуска в обращение)",
    "not_applicable_3_3_5": "не применяется (на ТС не представлены сообщения об официальном утверждении типа ТС)",
    "not_applicable_3_3_6": "не применяется (ТС имеет серийно произведенный кузов)",
    "not_applicable_a_1_2_1": "не применяется (на ТС отсутствует государственный регистрационный знак)",
    "not_applicable_a_1_2_2": "не применяется (на ТС отсутствует государственный регистрационный знак)",
    "not_applicable_a_1_2_3": "не применяется (на ТС отсутствует государственный регистрационный знак)",
    "not_applicable_a_1_2_4": "не применяется (на ТС отсутствует государственный регистрационный знак)",
    "not_applicable_a_2_1": "не применяется (ТС не используется для коммерческих перевозок)",
    "not_applicable_a_3_1_regulation": "не применяется (пункт Постановления Правительства)",
    "not_applicable_a_3_1_certified_emergency_call": "не применяется (ТС оборудовано сертифицированным устройством вызова экстренных оперативных служб)",
    "not_applicable_a_3_2": "не применяется (пункт Постановления Правительства)",
    "not_applicable_a_5_1_2_2": "не применяется (ТС оборудован двухконтурной тормозной системой. Запасная тормозная система входит в состав рабочей тормозной системы и не оснащается независимым органом управления)",
    "not_applicable_a_5_1_4_2_1": "не применяется (Удельная тормозная сила стояночной тормозной системы измерена в ходе проведения испытаний на тормозном стенде)",
    "not_applicable_a_5_5_1_3": "не применяется (ТС оборудован двухконтурной тормозной системой. Аварийная тормозная система входит в состав рабочей тормозной системы и не оснащается независимым органом управления)",
    "not_applicable_a_5_11_1": "не применяется (ТС не оборудовано пневматической тормозной системой)",
    "not_applicable_a_5_11_6": "не применяется (ТС не оборудовано регулятором тормозных сил)",
    "not_applicable_a_5_11_8": "не применяется (ТС не оборудовано регулятором тормозных сил)",
    "not_applicable_a_5_16": "не применяется (ТС не оборудовано пневматической тормозной системой)",
    "not_applicable_a_5": "не применяется (ТС не оборудовано пневматической тормозной системой)",
    "not_applicable_a_6_4": "не применяется (сервоприводы для включения и/или отключения устройства для предотвращения несанкционированного использования не используются)",
    "not_applicable_a_6_5": "не применяется (ТС не оснащено противоугонным устройством, блокирующим рулевое управление)",
    "not_applicable_a_7_3": "не применяется (в ТС отсутствует автономная от двигателя система отопления)",
    "not_applicable_a_7_5": "не применяется (в ТС отсутствует отопитель с выхлопной трубой)",
    "not_applicable_a_7_6": "не применяется (в ТС отсутствует обогревательный прибор с камерой сгорания)",
    "not_applicable_a_8_1": "не применяется (на ТС отсутствуют(один из вариантов): фонари, огни, фары, устройства, маркировки)",
    "not_applicable_a_8_7": "не применяется (в фарах ТС установлены источники света отличные от описанных в п. А.8.7)",
    "not_applicable_a_8_10_1": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "not_applicable_a_8_10_2": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "not_applicable_a_8_10_3": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "not_applicable_a_8_13_1_no_lamps": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "not_applicable_a_8_13_1_two_lamps": "не применяется (в ТС имеется два задних противотуманных фонаря)",
    "not_applicable_a_8_13_2": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "not_applicable_a_8_18_1": "отсутствие",
    "not_applicable_a_8_18_2": "отсутствие",
    "not_applicable_a_8_18_3": "отсутствие",
    "not_applicable_a_8_18_4": "отсутствие",
    "not_applicable_a_8_19": "не применяется (на ТС отсутствует светоотражающая маркировка)",
    "not_applicable_a_8_20_3": "не применяется (ТС не оснащено устройствами фароочистки  и автоматическим корректирующим устройством угла наклона фар (не предусмотрено конструкцией))",
    "not_applicable_a_8_20_8": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "not_applicable_a_8_24_1": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "not_applicable_a_8_24_2": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "not_applicable_a_8_24_3": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "not_applicable_a_8_25": "не применяется (в ТС отсутствуют стояночные огни)",
    "not_applicable_a_8_27": "не применяется (в ТС отсутствуют дневные ходовые огни)",
    "not_applicable_a_10_4": "не применяется (на ТС отсутствуют сдвоеные колеса",
    "not_applicable_a_10_5": "не применяется (на ТС установлены летние шины)",
    "not_applicable_a_10_6": "не применяется (на ТС установлены шины без шипов)",
    "not_applicable_a_10_7_3": "не применяется (на ТС установлены летние шины)",
    "not_applicable_a_10_9_1": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2_1": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2_2": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2_3": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2_4": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_2_5": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_10_9_3": "не применяется (на ТС не применяются восстановленные шины)",
    "not_applicable_a_11_16": "не применяется (ТС имеет четыре колеса)",
    "not_applicable_a_13_6": "не применяется (на ТС отсутствует сенсорный механизм, автоматически определяющий наличие детского удерживающего устройства)",
    "not_applicable_a_13_14": "не применяется (на ТС отсутствует двустворчатая дверная конструкция для обеспечения доступа к передним и задним сиденьям)",
    "not_applicable_a_16_2": "не применяется (на ТС отсутствуют эмблемы и другие декоративные объекты выступающее более чем на 10мм)",
    "not_applicable_a_16_11": "не применяется (на ТС отсутствуют поворотные ручки)",
    "not_applicable_a_16_12": "не применяется (на ТС отсутствуют поворотные ручки)",
    "not_applicable_a_16_13": "не применяется (на ТС отсутствуют стекла, открывающиеся наружу по отношению к внешней поверхности ТС)",
    "not_applicable_a_16_14": "не применяется (на ТС отсутствуют ободки и козырьки фар)",
    "not_applicable_a_16_15": "не применяется (на ТС отсутствуют кронштейны для домкрата)",
    "not_applicable_a_16_16": "не применяется (на ТС отсутствуют выступающие более чем на 10 мм выпускные трубы)",
    "not_applicable_a_16_17": "не применяется (на ТС отсутствуют подножки и ступеньки)",
    "not_applicable_a_17_2": "не применяется (на ТС болты, используемые для крепления рулевого колеса к ступице, не находятся снаружи)",
    "not_applicable_a_17_3": "не применяется (на рулевом колесе ТС отсутствуют непокрытые металлические спицы)",
    "not_applicable_a_18_3": "не применяется (на ТС отсутствуют полки для вещей)",
    "not_applicable_a_18_4_2": "не применяется (на ТС отсутствуют выступающие элементы крыши из жесткого материала)",
    "not_applicable_a_18_4_4": "не применяется (на ТС отсутствуют выступающие планки и ребра крыши из жесткого материала)",
    "not_applicable_a_18_5": "не применяется (на ТС отсутствует складывающаяся крыша)",
    "not_applicable_a_20_1": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_2": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_3": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_5": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_5_1_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_5_1_no_fixed_cap": "не применяется (на ТС отсутствует несъемная крышка наливной горловины топливного бака)",
    "not_applicable_a_20_5_2_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_5_2_no_vapor_protection": "не применяется (на ТС отсутствуют элементы конструкции, не допускающие утечки избыточных паров и топлива в случае отсутствия крышки наливной горловины)",
    "not_applicable_a_20_5_3": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_6": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_7": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_20_8": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_3_petrol": "не применяется (ТС оборудовано бензиновым двигателем)",
    "not_applicable_a_21_3_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_3_m1_under_3500kg": "не применяется (ТС категории М1 массой менее 3,5 т)",
    "not_applicable_a_21_4": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_5": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_6": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_7_diesel": "не применяется (ТС оборудовано дизельным двигателем)",
    "not_applicable_a_21_7_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_7_low_mileage": "не применяется (пробег ТС менее 3000 км)",
    "not_applicable_a_21_8_petrol": "не применяется (ТС оборудовано бензиновым двигателем)",
    "not_applicable_a_21_8_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_21_8_low_mileage": "не применяется (пробег ТС менее 3000 км)",
    "not_applicable_a_21_9_electric": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_22_3": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_22_4": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_22_5_1": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_2": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_3": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_4": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_5": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_6_1": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_6_2": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_22_5_6_3": "не применяется (ТС не оборудовано газобалонным оборудованием)",
    "not_applicable_a_23_1": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_23_2": "не применяется (ТС оборудовано только электродвигателем)",
    "not_applicable_a_24_6": "не применяется (ТС оборудовано электрической рулевой рейкой)",
    "not_applicable_a_26_7": "не применяется (на ТС отсутствует пневматическая подвеска)",
    "not_applicable_a_26_8": "не применяется (на ТС отсутствуют повреждения или изменения конструкции передних и задних бамперов ТС)",
    "not_applicable_a_26_12": "не применяется (на ТС отсутствует запасное колесо)",
    "not_applicable_stb_914_e_4_7": "не применяется (на ТС отсутствует государственный регистрационный знак)",
}


_ALTERNATE_REASON_CODES = {
    "a_3_1_regulation": "a_3_1",
    "a_3_1_certified_emergency_call": "a_3_1",
    "a_8_13_1_no_lamps": "a_8_13_1",
    "a_8_13_1_two_lamps": "a_8_13_1",
    "a_20_5_1_electric": "a_20_5_1",
    "a_20_5_1_no_fixed_cap": "a_20_5_1",
    "a_20_5_2_electric": "a_20_5_2",
    "a_20_5_2_no_vapor_protection": "a_20_5_2",
    "a_21_3_petrol": "a_21_3",
    "a_21_3_electric": "a_21_3",
    "a_21_3_m1_under_3500kg": "a_21_3",
    "a_21_7_diesel": "a_21_7",
    "a_21_7_electric": "a_21_7",
    "a_21_7_low_mileage": "a_21_7",
    "a_21_8_petrol": "a_21_8",
    "a_21_8_electric": "a_21_8",
    "a_21_8_low_mileage": "a_21_8",
    "a_21_9_electric": "a_21_9",
}


def _point_codes():
    codes = set()
    for placeholder in _EXCEL_REASON_OPTIONS:
        code = placeholder.removeprefix("not_applicable_")
        codes.add(_ALTERNATE_REASON_CODES.get(code, code))
    return codes


def build_applicability_values(protocol, measurement, light, dynamic_values):
    def output_key(code):
        suffix = code.removeprefix("a_")
        return f"applicable_{suffix}"

    values = {output_key(code): "не указано" for code in _point_codes()}

    def set_value(code, message):
        values[output_key(code)] = message

    def reason(code, option=None):
        suffix = f"_{option}" if option else ""
        return _EXCEL_REASON_OPTIONS[f"not_applicable_{code}{suffix}"]

    for reason_key, message in _EXCEL_REASON_OPTIONS.items():
        code = reason_key.removeprefix("not_applicable_")
        if (
            code in _ALTERNATE_REASON_CODES
            or not code.startswith(("a_", "stb_"))
            or code.startswith("a_1_")
        ):
            continue
        set_value(code, message)

    def positive_count(value):
        number = decimal_value(value)
        return number is not None and number > 0

    def is_fuel_petrol_like(value):
        return value in {"petrol", "hybrid"}

    for code in _point_codes():
        status = dynamic_values.get(f"result_{code}_status")
        if status is not None:
            set_value(code, status)

    full_result_keys = {
        "a_8_10_1": "full_result_a_8_10_1",
        "a_8_10_2": "full_result_a_8_10_2",
        "a_8_13_2": "full_result_a_8_13_2",
        "a_10_7_3": "full_result_a_10_7_3",
        "a_21_7": "full_result_a_21_7",
        "a_21_8": "full_result_a_21_8",
        "a_21_9": "full_result_a_21_9",
    }
    for code, result_key in full_result_keys.items():
        if result_key in dynamic_values:
            set_value(code, dynamic_values[result_key])

    registration_number = getattr(protocol, "registration_number", None)
    registration_missing = not registration_number or str(registration_number).strip() in {
        "-",
        "отсутствует",
    }
    registration_status = reason("a_1_2_1") if registration_missing else "соответствует"
    for code in ("a_1_2_1", "a_1_2_2", "a_1_2_3", "a_1_2_4"):
        set_value(code, registration_status)
    set_value(
        "stb_914_e_4_7",
        reason("stb_914_e_4_7") if registration_missing else "соответствует",
    )

    emergency_call_present = getattr(measurement, "glonass_button_present", None) is True
    set_value(
        "a_3_1",
        reason("a_3_1_certified_emergency_call")
        if emergency_call_present
        else reason("a_3_1_regulation"),
    )

    light_counts = [
        getattr(light, field, None)
        for field in (
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
        )
    ]
    if any(positive_count(count) for count in light_counts):
        set_value("a_8_1", "соответствует")
    elif all(count is not None for count in light_counts):
        set_value("a_8_1", reason("a_8_1"))

    front_fog_present = positive_count(getattr(light, "front_fog_count", None))
    rear_fog_present = positive_count(getattr(light, "rear_fog_count", None))
    if "full_result_a_8_10_1" not in dynamic_values:
        set_value(
            "a_8_10_1",
            "соответствует" if front_fog_present else reason("a_8_10_1"),
        )
    if "full_result_a_8_10_2" not in dynamic_values:
        set_value(
            "a_8_10_2",
            "соответствует" if front_fog_present else reason("a_8_10_2"),
        )
    if "full_result_a_8_13_2" not in dynamic_values:
        set_value(
            "a_8_13_2",
            "соответствует" if rear_fog_present else reason("a_8_13_2"),
        )
    if "full_result_a_10_7_3" not in dynamic_values:
        set_value(
            "a_10_7_3",
            reason("a_10_7_3")
            if getattr(protocol, "tire_season", None) == "summer"
            else "соответствует"
            if getattr(protocol, "tire_season", None) == "winter"
            else "не указано",
        )

    fuel_type = getattr(measurement, "fuel_type", None)
    electric = fuel_type == "electric"
    electric_only_reasons = (
        "a_20_1",
        "a_20_2",
        "a_20_3",
        "a_20_5",
        "a_20_5_3",
        "a_20_6",
        "a_20_7",
        "a_20_8",
        "a_21_4",
        "a_21_5",
        "a_21_6",
        "a_22_3",
        "a_22_4",
        "a_23_1",
        "a_23_2",
    )
    for code in electric_only_reasons:
        set_value(code, reason(code) if electric else "соответствует")

    set_value(
        "a_20_5_1",
        reason("a_20_5_1_electric")
        if electric
        else reason("a_20_5_1_no_fixed_cap"),
    )
    set_value(
        "a_20_5_2",
        reason("a_20_5_2_electric")
        if electric
        else reason("a_20_5_2_no_vapor_protection"),
    )

    if is_fuel_petrol_like(fuel_type):
        a_21_3 = reason("a_21_3_petrol")
    elif electric:
        a_21_3 = reason("a_21_3_electric")
    else:
        a_21_3 = "не указано"
    set_value("a_21_3", a_21_3)

    mileage = decimal_value(getattr(measurement, "mileage_km", None))
    if electric:
        set_value("a_21_9", reason("a_21_9_electric"))
    elif mileage is None or mileage >= 3000:
        set_value("a_21_9", "более 3000 км")
    else:
        set_value("a_21_9", "менее 3000 км")

    category = getattr(protocol, "vehicle_category", None)
    if category in {"M1", "N1"}:
        set_value("a_11_16", reason("a_11_16"))

    if electric:
        set_value("a_23_1", reason("a_23_1"))
    elif fuel_type in {"petrol", "diesel", "hybrid"}:
        set_value(
            "a_23_1",
            "Соответствует требованиям\n"
            "ТР ТС 018/2011\n"
            "Приложения N 8 п.9.9\n"
            "Требование: не более 96 дБА\n"
            "Результат при поддержании целевой частоты вращения: "
            f"{dynamic_values.get('exhaust_noise_constant_db', '-')} дБА ± "
            f"{dynamic_values.get('u_exhaust_noise_constant_db', '-')} дБА\n"
            "Результат в режиме замедления: "
            f"{dynamic_values.get('exhaust_noise_deceleration_db', '-')} дБА ± "
            f"{dynamic_values.get('u_exhaust_noise_deceleration_db', '-')} дБА",
        )
    elif fuel_type in {"petrol", "diesel", "hybrid"}:
        set_value(
            "a_23_1",
            "Соответствует требованиям\n"
            "ТР ТС 018/2011\n"
            "Приложения N 8 п.9.9\n"
            "Требование: не более 96 дБА\n"
            "Результат при поддержании целевой частоты вращения: "
            f"{dynamic_values.get('exhaust_noise_constant_db', '-')} дБА ± "
            f"{dynamic_values.get('u_exhaust_noise_constant_db', '-')} дБА\n"
            "Результат в режиме замедления: "
            f"{dynamic_values.get('exhaust_noise_deceleration_db', '-')} дБА ± "
            f"{dynamic_values.get('u_exhaust_noise_deceleration_db', '-')} дБА",
        )

    return values
