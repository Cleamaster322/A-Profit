WHEEL_FORMULA_LABELS = {
    "4x2_front": "4x2 — передний",
    "4x2_rear": "4x2 — задний",
    "4x4": "4x4 — полный",
}

ENGINE_LAYOUT_LABELS = {
    "transverse": "Поперечное",
    "longitudinal": "Продольное",
}

CYLINDER_LAYOUT_LABELS = {
    "inline": "Рядное",
    "opposed": "Оппозитное",
    "v_shape": "V-образное",
}

FUEL_TYPE_LABELS = {
    "petrol": "Бензин",
    "diesel": "Дизель",
    "hybrid": "Гибрид",
    "electric": "Электро",
}

STEERING_BOOSTER_LABELS = {
    "hydraulic": "гидромеханический",
    "electric": "электромеханический",
}

TRANSMISSION_LABELS = {
    "automatic": "Автомат",
    "variator": "Вариатор",
    "manual": "Механика",
    "robot": "Робот",
    "reductor": "Редуктор",
}

SERVICE_BRAKE_LABELS = {
    "disc_disc": "Дисковая/дисковая",
    "disc_drum": "Дисковая/барабанная",
    "other": "Другое",
}

PARKING_BRAKE_LABELS = {
    "mechanical_hand": "Механический ручной",
    "mechanical_pedal": "Механический педаль",
    "electric": "Электрический",
    "other": "Другое",
}

TIRE_SEASON_LABELS = {
    "summer": "Лето",
    "winter": "Зима",
}

FUEL_TANK_MEASURE_LABELS = {
    "fixed_cap": "Несъемная крышка",
    "structural_elements": "Элементы конструкции",
    "other_measure": "Любая другая мера",
}


def label(mapping, value, default=""):
    if value is None or value == "":
        return default

    return mapping.get(value, str(value))