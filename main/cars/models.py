from django.conf import settings
from django.db import models
from django.utils import timezone

# =========================
# Общие mixin-классы
# =========================

class DashFieldsMixin(models.Model):
    """
    Хранит список полей, в которых пользователь явно поставил прочерк "-".

    Логика:
    - значение поля в БД остается NULL;
    - если имя поля есть в dash_fields, frontend при загрузке показывает "-";
    - если значение NULL и имени поля нет в dash_fields, frontend показывает пустую строку.

    Это нужно, чтобы отличать:
    1) поле ещё не заполняли;
    2) пользователь сознательно поставил прочерк.
    """
    dash_fields = models.JSONField(default=list, blank=True)

    class Meta:
        abstract = True


# =========================
# Автомобильный справочник
# =========================

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=255)

    class Meta:
        db_table = 'brands'

    def __str__(self):
        return self.name


class Model(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING, db_column='brand_id')
    name = models.CharField(max_length=100)
    link = models.URLField(max_length=255)

    class Meta:
        db_table = 'models'

    def __str__(self):
        return self.name


class Generation(models.Model):
    id = models.AutoField(primary_key=True)
    model = models.ForeignKey(Model, on_delete=models.DO_NOTHING, db_column='model_id')
    name = models.CharField(max_length=255)
    link = models.URLField(max_length=255)
    body_code = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    body_type = models.CharField(max_length=100, null=True, blank=True)
    is_hybrid = models.BooleanField(default=False)
    generation_num = models.IntegerField(null=True, blank=True)
    restyling_num = models.IntegerField(null=True, blank=True)
    date_start = models.CharField(max_length=11, null=True, blank=True)
    date_end = models.CharField(max_length=11, null=True, blank=True)
    image_path = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'generations'

    def __str__(self):
        return self.name


class Configuration(models.Model):
    id = models.AutoField(primary_key=True)
    generation = models.ForeignKey(Generation, on_delete=models.DO_NOTHING, db_column='generation_id')
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(max_length=255, null=True, blank=True)
    engine_name = models.CharField(max_length=100, null=True, blank=True)
    date_start = models.CharField(max_length=11, null=True, blank=True)
    date_end = models.CharField(max_length=11, null=True, blank=True)

    class Meta:
        db_table = 'configurations'

    def __str__(self):
        return self.name or f"Configuration #{self.id}"


class CarData(models.Model):
    id = models.AutoField(primary_key=True)
    configuration = models.ForeignKey(Configuration, on_delete=models.DO_NOTHING, db_column='configuration_id')

    configuration_name = models.CharField(max_length=255, null=True, blank=True)
    manufacture_year = models.IntegerField(null=True, blank=True)

    front_tires = models.CharField(max_length=50, null=True, blank=True)
    rear_tires = models.CharField(max_length=50, null=True, blank=True)

    fuel_type = models.CharField(max_length=50, null=True, blank=True)
    transmission = models.CharField(max_length=50, null=True, blank=True)
    drive_type = models.CharField(max_length=50, null=True, blank=True)

    seats_count = models.CharField(max_length=50, null=True, blank=True)
    clearance = models.IntegerField(null=True, blank=True)

    # Тип кузова: Хэтчбек, Седан, Универсал и т.д.
    body_type = models.CharField(max_length=255, null=True, blank=True)

    # Маркировка кузова из справочника: 5BA-B43W, CBA-TD54W и т.д.
    # В протокол нужно передавать очищенное значение без японского префикса:
    # 5BA-B43W -> B43W
    # CBA-TD54W -> TD54W
    body_mark = models.CharField(max_length=100, null=True, blank=True)

    vehicle_weight_kg = models.IntegerField(null=True, blank=True)

    engine_model = models.CharField(max_length=255, null=True, blank=True)
    engine_capacity = models.FloatField(null=True, blank=True)
    engine_power_hp = models.IntegerField(null=True, blank=True)
    engine_power_kw = models.IntegerField(null=True, blank=True)
    cylinder_layout = models.CharField(max_length=50, null=True, blank=True)
    cylinders_count = models.IntegerField(null=True, blank=True)
    turbo_present = models.BooleanField(null=True, blank=True)

    front_brakes = models.CharField(max_length=255, null=True, blank=True)
    rear_brakes = models.CharField(max_length=255, null=True, blank=True)

    vehicle_length_mm = models.IntegerField(null=True, blank=True)
    vehicle_width_mm = models.IntegerField(null=True, blank=True)
    vehicle_height_mm = models.IntegerField(null=True, blank=True)

    @property
    def normalized_body_mark(self):
        """
        Очищенная маркировка кузова для протокола.

        Примеры:
        5BA-B43W  -> B43W
        CBA-TD54W -> TD54W
        DBA-Z12   -> Z12
        B43W      -> B43W
        """
        if not self.body_mark:
            return None

        value = str(self.body_mark).strip()

        if '-' in value:
            return value.split('-')[-1].strip()

        return value

    class Meta:
        db_table = 'car_data'
        verbose_name = 'Car Data'
        verbose_name_plural = 'Car Data'

    def __str__(self):
        return f"{self.configuration.name} - {self.fuel_type}"


# =========================
# Протокол
# =========================

class Protocol(DashFieldsMixin, models.Model):
    STATUS_CHOICES = [
        ('measurement', 'Работа замерщика'),
        ('operator', 'Работа оператора'),
        ('review', 'На проверке'),
        ('revision', 'На доработке'),
        ('approved', 'Утверждён'),
        ('cancelled', 'Отменён'),
    ]

    SUPERCHARGER_CHOICES = [
        ('absent', 'Отсутствует'),
        ('compressor', 'Компрессор'),
        ('turbo', 'Турбина'),
        ('twin_turbo', 'Твин-турбо'),
    ]

    OWNER_TYPE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('company', 'Компания'),
    ]

    VEHICLE_CATEGORY_CHOICES = [
        ('M1', 'M1'),
        ('N1', 'N1'),
    ]

    TIRE_SEASON_CHOICES = [
        ('summer', 'Лето'),
        ('winter', 'Зима'),
    ]

    id = models.BigAutoField(primary_key=True)
    protocol_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    protocol_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='measurement')
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locked_protocols",
        db_column="locked_by_id",
    )

    locked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column="locked_at",
    )


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name='protocols',
        db_column='user_id'
    )
    model = models.ForeignKey(
        Model,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols',
        db_column='model_id',
    )
    generation = models.ForeignKey(
        Generation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols',
        db_column='generation_id',
    )
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocols',
        db_column='configuration_id',
    )
    car = models.ForeignKey(
        CarData,
        on_delete=models.RESTRICT,
        related_name='protocols',
        db_column='car_id',
        null=True,
        blank=True
    )

    owner_type = models.CharField(max_length=20, choices=OWNER_TYPE_CHOICES, default='individual')

    # Данные заказчика
    owner_name = models.CharField(max_length=255, null=True, blank=True)

    owner_last_name = models.CharField(max_length=150, null=True, blank=True)
    owner_first_name = models.CharField(max_length=150, null=True, blank=True)
    owner_middle_name = models.CharField(max_length=150, null=True, blank=True)

    owner_address = models.CharField(max_length=500, blank=True, null=True)
    owner_document = models.CharField(max_length=255, blank=True, null=True)
    owner_phone = models.CharField(max_length=50, blank=True, null=True)

    # Изготовитель
    manufacturer_info = models.TextField(blank=True, null=True)

    appendix_number = models.CharField(max_length=100, blank=True, null=True)
    commercial_name = models.CharField(max_length=255, blank=True, null=True)

    brand_name = models.CharField(max_length=255, blank=True, null=True)
    vehicle_category = models.CharField(max_length=2, choices=VEHICLE_CATEGORY_CHOICES, blank=True, null=True)
    body_type = models.CharField(max_length=255, blank=True, null=True)
    supercharger = models.CharField(
        max_length=20,
        choices=SUPERCHARGER_CHOICES,
        blank=True,
        null=True,
    )

    vin = models.CharField(max_length=50, blank=True, null=True)
    chassis_number = models.CharField(max_length=50, blank=True, null=True)
    body_number = models.CharField(max_length=50, blank=True, null=True)
    engine_number = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)

    wheel_marking_front = models.CharField(max_length=100, blank=True, null=True)
    wheel_marking_rear = models.CharField(max_length=100, blank=True, null=True)
    tire_season = models.CharField(max_length=10, choices=TIRE_SEASON_CHOICES, blank=True, null=True)
    has_spikes = models.BooleanField(blank=True, null=True)

    manufacture_year = models.IntegerField(blank=True, null=True)
    manufacture_date = models.DateField(blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    inspection_place = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    returned_for_revision = models.BooleanField(default=False)

    revision_comment = models.TextField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="cancelled_protocols"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'protocols'
        ordering = ['-created_at']

    def __str__(self):
        return self.protocol_number or f"Protocol #{self.id}"


# =========================
# ProtocolMeasurement
# =========================

class ProtocolMeasurement(DashFieldsMixin, models.Model):
    WHEEL_FORMULA_CHOICES = [
        ('4x2_front', '4x2 передний'),
        ('4x2_rear', '4x2 задний'),
        ('4x4', '4x4 полный'),
    ]

    ENGINE_LAYOUT_CHOICES = [
        ('transverse', 'Поперечное'),
        ('longitudinal', 'Продольное'),
    ]

    CYLINDER_LAYOUT_CHOICES = [
        ('inline', 'Рядное'),
        ('opposed', 'Оппозитное'),
        ('v_shape', 'V-образное'),
    ]

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('hybrid', 'Гибрид'),
        ('electric', 'Электро'),
    ]

    STEERING_BOOSTER_TYPE_CHOICES = [
        ('hydraulic', 'Гидромеханический'),
        ('electric', 'Электромеханический'),
    ]

    TRANSMISSION_TYPE_CHOICES = [
        ('automatic', 'Автомат'),
        ('variator', 'Вариатор'),
        ('manual', 'Механика'),
        ('robot', 'Робот'),
        ('reductor', 'Редуктор'),
    ]

    FUEL_TANK_LEAK_PROTECTION_CHOICES = [
        ('fixed_cap', 'Несъемная крышка'),
        ('structural_elements', 'Элементы конструкции'),
        ('other_measure', 'Любая другая мера'),
    ]

    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='measurement',
        db_column='protocol_id'
    )

    # Конструктив
    wheel_formula = models.CharField(max_length=20, choices=WHEEL_FORMULA_CHOICES, blank=True, null=True)
    mufflers_count = models.IntegerField(blank=True, null=True)
    seats_count = models.CharField(max_length=50, blank=True, null=True)
    steps_present = models.BooleanField(blank=True, null=True)

    # Двигатель
    engine_model = models.CharField(max_length=255, blank=True, null=True)
    engine_power_kw = models.IntegerField(blank=True, null=True)
    engine_layout = models.CharField(max_length=20, choices=ENGINE_LAYOUT_CHOICES, blank=True, null=True)
    cylinder_layout = models.CharField(max_length=20, choices=CYLINDER_LAYOUT_CHOICES, blank=True, null=True)
    cylinders_count = models.IntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, blank=True, null=True)
    turbo_present = models.BooleanField(blank=True, null=True)

    # Рулевое управление
    steering_booster_type = models.CharField(
        max_length=20,
        choices=STEERING_BOOSTER_TYPE_CHOICES,
        blank=True,
        null=True
    )
    steering_backlash_deg = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # Трансмиссия
    transmission_type = models.CharField(
        max_length=20,
        choices=TRANSMISSION_TYPE_CHOICES,
        blank=True,
        null=True
    )

    # Остаточная глубина рисунка протектора
    tire_depth_fl_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tire_depth_fr_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tire_depth_rl_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tire_depth_rr_mm = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    # Кузов и наружные элементы
    bumper_bends_to_body = models.BooleanField(blank=True, null=True)
    bumper_to_body_distance_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    opening_roof_present = models.BooleanField(blank=True, null=True)

    fuel_tank_leak_protection_measure = models.CharField(
        max_length=50,
        choices=FUEL_TANK_LEAK_PROTECTION_CHOICES,
        blank=True,
        null=True
    )

    protruding_elements_doors_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    protruding_elements_other_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Стекла
    glass_transparency_right_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    glass_transparency_left_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    glass_transparency_windshield_pct = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sun_strip_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Скорость
    speed_by_speedometer_kmh = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    actual_speed_kmh = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # Шум отработавших газов
    exhaust_noise_constant_db = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    exhaust_noise_deceleration_db = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # Содержание CO
    co_min_pct = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    co_max_pct = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)

    # Коэффициент поглощения света
    light_absorption_1 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    light_absorption_2 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    light_absorption_3 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    light_absorption_4 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    light_absorption_5 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    light_absorption_6 = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)

    # Габариты и масса
    vehicle_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vehicle_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vehicle_height_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vehicle_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Нагрузка на ось
    axle1_load_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    axle2_load_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Нагрузка на ось на тормозном стенде
    stand_axle1_load_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stand_axle2_load_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Новые поля под актуальную версию протокола
    mileage_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    spare_wheel_present = models.BooleanField(blank=True, null=True)
    steering_lock_present = models.BooleanField(blank=True, null=True)
    gas_equipment_present = models.BooleanField(blank=True, null=True)
    glonass_button_present = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'protocol_measurements'


# =========================
# ProtocolBrake
# =========================

class ProtocolBrake(DashFieldsMixin, models.Model):
    SERVICE_BRAKE_TYPE_CHOICES = [
        ('disc_disc', 'Дисковая/дисковая'),
        ('disc_drum', 'Дисковая/барабанная'),
        ('other', 'Другое'),
    ]

    PARKING_BRAKE_TYPE_CHOICES = [
        ('mechanical_hand', 'Механический ручной'),
        ('mechanical_pedal', 'Механический педаль'),
        ('electric', 'Электрический'),
        ('other', 'Другое'),
    ]

    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='brake',
        db_column='protocol_id'
    )

    service_brake_type = models.CharField(max_length=30, choices=SERVICE_BRAKE_TYPE_CHOICES, blank=True, null=True)
    parking_brake_type = models.CharField(max_length=30, choices=PARKING_BRAKE_TYPE_CHOICES, blank=True, null=True)

    service_brake_control_force_axle1_n = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_brake_control_force_axle2_n = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    parking_brake_control_force_n = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    axle_1_brake_difference_pct = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    axle_2_brake_difference_pct = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    service_brake_front_left_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    service_brake_front_right_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    service_brake_rear_left_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    service_brake_rear_right_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    parking_brake_left_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    parking_brake_right_kn = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)

    class Meta:
        db_table = 'protocol_brakes'


# =========================
# ProtocolLight
# =========================

class ProtocolLight(DashFieldsMixin, models.Model):
    HEADLIGHT_TYPE_CHOICES = [
        ('halogen', 'Галоген'),
        ('xenon', 'Ксенон'),
        ('led', 'LED'),
        ('other', 'Другое'),
    ]

    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='light',
        db_column='protocol_id'
    )

    # Количество и цвет внешних световых приборов
    low_beam_count = models.IntegerField(blank=True, null=True)
    low_beam_color = models.CharField(max_length=50, blank=True, null=True)

    high_beam_count = models.IntegerField(blank=True, null=True)
    high_beam_color = models.CharField(max_length=50, blank=True, null=True)

    front_fog_count = models.IntegerField(blank=True, null=True)
    front_fog_color = models.CharField(max_length=50, blank=True, null=True)

    reverse_light_count = models.IntegerField(blank=True, null=True)
    reverse_light_color = models.CharField(max_length=50, blank=True, null=True)

    turn_signal_count = models.IntegerField(blank=True, null=True)
    turn_signal_color = models.CharField(max_length=50, blank=True, null=True)

    front_position_light_count = models.IntegerField(blank=True, null=True)
    front_position_light_color = models.CharField(max_length=50, blank=True, null=True)

    rear_position_light_count = models.IntegerField(blank=True, null=True)
    rear_position_light_color = models.CharField(max_length=50, blank=True, null=True)

    main_brake_signal_count = models.IntegerField(blank=True, null=True)
    main_brake_signal_color = models.CharField(max_length=50, blank=True, null=True)

    additional_brake_signal_count = models.IntegerField(blank=True, null=True)
    additional_brake_signal_color = models.CharField(max_length=50, blank=True, null=True)

    rear_fog_count = models.IntegerField(blank=True, null=True)
    rear_fog_color = models.CharField(max_length=50, blank=True, null=True)

    plate_light_count = models.IntegerField(blank=True, null=True)
    plate_light_color = models.CharField(max_length=50, blank=True, null=True)

    daytime_running_light_count = models.IntegerField(blank=True, null=True)
    daytime_running_light_color = models.CharField(max_length=50, blank=True, null=True)

    # Передние стояночные огни
    parking_light_count = models.IntegerField(blank=True, null=True)
    parking_light_color = models.CharField(max_length=50, blank=True, null=True)

    # Задние стояночные огни
    rear_parking_light_count = models.IntegerField(blank=True, null=True)
    rear_parking_light_color = models.CharField(max_length=50, blank=True, null=True)

    # Адаптивная система переднего освещения
    adaptive_front_lighting_count = models.IntegerField(blank=True, null=True)
    adaptive_front_lighting_color = models.CharField(max_length=50, blank=True, null=True)

    # Тип фар
    headlight_type = models.CharField(max_length=20, choices=HEADLIGHT_TYPE_CHOICES, blank=True, null=True)

    # Установка фар ближнего света по высоте
    low_beam_upper_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    low_beam_lower_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Установка ПТФ
    fog_light_upper_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fog_light_lower_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fog_light_left_distance_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fog_light_right_distance_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Установка основных сигналов торможения
    brake_signal_upper_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brake_signal_lower_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brake_signal_left_distance_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brake_signal_right_distance_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Установка дополнительного сигнала торможения
    additional_brake_signal_from_glass_edge_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    additional_brake_signal_from_support_surface_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    additional_brake_signal_optical_center_shift_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # Установка задних ПТФ по высоте
    rear_fog_upper_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rear_fog_lower_point_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Омыватели фар
    headlight_washer_present = models.BooleanField(blank=True, null=True)

    # Сила света фар
    left_34v_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    left_52h_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    left_high_beam_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    right_34v_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    right_52h_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    right_high_beam_cd = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    # Частота мерцания указателей поворота / аварийной сигнализации
    turn_signal_frequency_per_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    turn_signal_frequency_hz = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'protocol_lights'


# =========================
# ProtocolPhoto
# =========================

class ProtocolPhoto(models.Model):
    PHOTO_TYPE_CHOICES = [
        ('front_view', 'Фото спереди'),
        ('rear_view', 'Фото сзади'),
        ('left_view', 'Фото слева'),
        ('right_view', 'Фото справа'),
        ('vin_photo', 'Фото VIN'),
        ('nameplate_photo', 'Фото шильдика'),
        ('tire_size_label_photo', 'Фото бирки размера колес'),
        ('odometer_photo', 'Фото пробега'),
        ('gas_test_photo', 'Фото испытаний: газы'),
        ('noise_test_photo', 'Фото испытаний: шум'),
        ('stand_test_photo', 'Фото испытаний: стенд'),
        ('other', 'Другое'),
    ]

    id = models.BigAutoField(primary_key=True)

    protocol = models.ForeignKey(
        Protocol,
        on_delete=models.CASCADE,
        related_name='photos',
        db_column='protocol_id'
    )

    photo_type = models.CharField(max_length=50, choices=PHOTO_TYPE_CHOICES, default='other')
    file_path = models.CharField(max_length=500, blank=True, null=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'protocol_photos'
        ordering = ['sort_order', 'id']


# =========================
# ProtocolTestCondition
# =========================

class ProtocolTestCondition(DashFieldsMixin, models.Model):
    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='test_conditions',
        db_column='protocol_id'
    )

    ambient_temperature_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    relative_humidity_pct = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    atmospheric_pressure_kpa = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'protocol_test_conditions'


# =========================
# ProtocolRoadCondition
# =========================

class ProtocolRoadCondition(DashFieldsMixin, models.Model):
    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='road_conditions',
        db_column='protocol_id'
    )

    road_ambient_temperature_c = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    road_relative_humidity_pct = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'protocol_road_conditions'


# =========================
# ProtocolPowerSupply
# =========================

class ProtocolPowerSupply(DashFieldsMixin, models.Model):
    id = models.BigAutoField(primary_key=True)

    protocol = models.OneToOneField(
        Protocol,
        on_delete=models.CASCADE,
        related_name='power_supply',
        db_column='protocol_id'
    )

    frequency_hz = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    phase_a_n_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    phase_b_n_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    phase_c_n_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    phase_ab_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    phase_bc_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    phase_ac_voltage_v = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'protocol_power_supply'