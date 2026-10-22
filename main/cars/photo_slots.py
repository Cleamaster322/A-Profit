"""
Фотофиксация протокола: фиксированный набор фото по схеме
templates/НОВЫЕ/ФОТО для нового протокола ВЛАД.xlsx.

Порядок списка — порядок на сайте и в DOCX. group — после какого блока страницы
протокола показывается фото. Коды старых типов (vin_photo, front_view, stand_test_photo
и т. д.) сохранены, чтобы уже загруженные фото попали в свои слоты.
"""

AFTER_CONDITIONS = 'after_conditions'
AFTER_STEERING_TRANSMISSION = 'after_steering_transmission'
AFTER_BRAKES = 'after_brakes'
AFTER_LIGHTS_GEOMETRY = 'after_lights_geometry'

PHOTO_SLOTS = [
    # После блока «2. Условия проведения испытаний»
    ('acceptance_photo', 'Приемка ТС', 'Эксперт с открытым капотом ТС', AFTER_CONDITIONS),
    ('vin_photo', 'Идентификационный номер (VIN) или серийный (заводской) номер', '', AFTER_CONDITIONS),
    ('nameplate_photo', 'Шилдик завода изготовителя', '', AFTER_CONDITIONS),
    ('tire_size_label_photo', 'Шилдик размер колес', '', AFTER_CONDITIONS),
    (
        'air_conditioner_photo',
        'Проверка состава кондиционера',
        'Бирка с № фреона. Если нет то эксперт с открытым капотом ТС',
        AFTER_CONDITIONS,
    ),
    ('odometer_photo', 'Одометр', '', AFTER_CONDITIONS),
    (
        'completeness_photo',
        'Проверка требований комплектности',
        'Эксперт поднимает крышку подпола в багажнике ТС',
        AFTER_CONDITIONS,
    ),
    (
        'fire_safety_photo',
        'Проверка требований пожарной безопасности',
        'Эксперт в смотровой яме. Делаем фото днища ТС где бензобак',
        AFTER_CONDITIONS,
    ),
    ('chassis_photo', 'Проверка ходовой части', 'Вид ТС снизу (перед авто)', AFTER_CONDITIONS),
    (
        'steering_suspension_photo',
        'Проверка рулевого управления и подвески',
        'Эксперт выставляет люфтометр перед ТС',
        AFTER_CONDITIONS,
    ),
    (
        'tire_marking_photo',
        'Маркировка шин',
        'Фото маркировки размера шины (только размер)',
        AFTER_CONDITIONS,
    ),

    # После блока «6. Рулевое управление и трансмиссия»
    (
        'stand_test_photo',
        'Испытания на тормозном стенде',
        'Вид спереди. ТС передними колесами на тормозном стенде',
        AFTER_STEERING_TRANSMISSION,
    ),

    # После блока «7. Тормозная система»
    ('anti_theft_photo', 'Проверка противоугонных устройств', 'Руки эксперта на руле ТС', AFTER_BRAKES),
    (
        'seat_belts_photo',
        'Проверка ремней безопасности',
        'Эксперт пристегивается ремнем безопасности',
        AFTER_BRAKES,
    ),
    ('front_view', 'Вид спереди', '', AFTER_BRAKES),
    ('rear_view', 'Вид сзади', '', AFTER_BRAKES),
    ('left_view', 'Вид слева', '', AFTER_BRAKES),
    ('right_view', 'Вид справа', '', AFTER_BRAKES),
    ('seats_photo', 'Проверка сидений', 'Ручка регулировки сиденья ТС с рукой эксперта', AFTER_BRAKES),
    (
        'door_locks_photo',
        'Проверка замков дверей',
        'Эксперт на сидении толкает дверь наружу, динамометр на панели ТС',
        AFTER_BRAKES,
    ),
    (
        'steering_injury_photo',
        'Проверка травмобезопасности рулевого управления',
        'Эксперт на сидении, руки на руле ТС в одежде с длинными рукавами',
        AFTER_BRAKES,
    ),
    (
        'interior_injury_photo',
        'Проверка травмобезопасности внутреннего оборудования',
        'Эксперт катает Шар 165 мм внутри салона ТС по потолку',
        AFTER_BRAKES,
    ),
    (
        'steering_backlash_photo',
        'Измерение суммарного люфта в рулевом управлении',
        'Эксперт на сидении, ИСЛ-М на руле ТС',
        AFTER_BRAKES,
    ),
    (
        'dimensions_photo',
        'Измерение габаритов ТС',
        'Эксперт держит строительный уровень (2м) на крыше ТС',
        AFTER_BRAKES,
    ),
    (
        'external_projections_photo',
        'Проверка травмобезопасности наружных выступов',
        'Эксперт катает Шар 100 мм в районе бампера ТС',
        AFTER_BRAKES,
    ),

    # После блока «9. Геометрия установки световых приборов»
    (
        'glass_transmission_photo',
        'Измерение светопропускания стекла',
        'Эксперт замеряет Тоником светопропускание стекла',
        AFTER_LIGHTS_GEOMETRY,
    ),
    ('noise_test_photo', 'Измерение уровня шума', 'ТС с шумомером + шаблон', AFTER_LIGHTS_GEOMETRY),
    (
        'gas_test_photo',
        'Измерение параметров отработавших газов',
        'Зонд в выхлопной трубе ТС, на фоне тумбочка с прибором',
        AFTER_LIGHTS_GEOMETRY,
    ),
    (
        'headlight_intensity_photo',
        'Измерение силы света фар',
        'Эксперт возле ИПФ, на ТС включены фары',
        AFTER_LIGHTS_GEOMETRY,
    ),
    (
        'emergency_call_photo',
        'Проверка УВЭОС',
        'Если есть Глонасс. Фото эксперта нажимающего кнопку',
        AFTER_LIGHTS_GEOMETRY,
    ),
    (
        'speed_photo',
        'Измерение скорости ТС',
        'Эксперт устанавливает ИСД на ТС на площадке ОП-1',
        AFTER_LIGHTS_GEOMETRY,
    ),
]

PHOTO_SLOT_CODES = [code for code, _, _, _ in PHOTO_SLOTS]
PHOTO_TYPE_CHOICES = [(code, title) for code, title, _, _ in PHOTO_SLOTS]
PHOTO_SLOT_TITLES = dict(PHOTO_TYPE_CHOICES)
PHOTO_SLOT_ORDER = {code: index for index, code in enumerate(PHOTO_SLOT_CODES)}


def slot_photos(protocol):
    """Фото протокола из схемы в порядке слотов; старые типы («Другое» и т. п.) отбрасываются."""
    photos = protocol.photos.filter(photo_type__in=PHOTO_SLOT_CODES)
    return sorted(photos, key=lambda photo: (PHOTO_SLOT_ORDER[photo.photo_type], photo.id))


def photo_slots_payload():
    return [
        {'photo_type': code, 'title': title, 'description': description, 'group': group}
        for code, title, description, group in PHOTO_SLOTS
    ]
