from uuid import uuid4

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.conf import settings

from .models import (
    Brand,
    Model,
    Generation,
    Configuration,
    CarData,
    Protocol,
    ProtocolMeasurement,
    ProtocolBrake,
    ProtocolLight,
    ProtocolPhoto,
    ProtocolTestCondition,
    ProtocolRoadCondition,
    ProtocolPowerSupply,
)


# =========================
# Общие helpers
# =========================

def normalize_body_mark_value(value):
    """
    Преобразует японскую маркировку кузова в код кузова для протокола.

    Примеры:
    5BA-B43W  -> B43W
    CBA-TD54W -> TD54W
    DBA-Z12   -> Z12
    B43W      -> B43W
    """
    if not value:
        return None

    value = str(value).strip()

    if '-' in value:
        return value.split('-')[-1].strip()

    return value


class DashFieldsSerializerMixin:
    """
    Общая проверка dash_fields для блоков протокола.

    dash_fields хранит имена полей, где пользователь явно поставил "-".

    Логика:
    - значение самого поля сохраняется как NULL;
    - имя поля добавляется в dash_fields;
    - при повторной загрузке frontend видит NULL + имя в dash_fields и показывает "-";
    - если NULL есть, но имени в dash_fields нет, frontend показывает пустую строку.
    """

    def validate_dash_fields(self, value):
        if value in (None, ''):
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError(
                'dash_fields должен быть списком строк'
            )

        cleaned = []

        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError(
                    'Каждое значение в dash_fields должно быть строкой'
                )

            field_name = item.strip()

            if field_name and field_name not in cleaned:
                cleaned.append(field_name)

        return cleaned


# =========================
# Справочник автомобилей
# =========================

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'


class GenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = '__all__'


class GenerationCardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Generation
        fields = [
            'id',
            'model',
            'name',
            'link',
            'body_code',
            'region',
            'body_type',
            'is_hybrid',
            'generation_num',
            'restyling_num',
            'date_start',
            'date_end',
            'image_path',
            'image_url',
        ]

    def normalize_image_path(self, value):
        if not value:
            return None

        value = str(value).strip().replace("\\", "/")

        if value.startswith("http://") or value.startswith("https://"):
            return value

        if "/main/media/" in value:
            value = value.split("/main/media/", 1)[1]
        elif value.startswith("main/media/"):
            value = value.replace("main/media/", "", 1)
        elif value.startswith("/main/media/"):
            value = value.replace("/main/media/", "", 1)
        elif "/media/" in value:
            value = value.split("/media/", 1)[1]

        return value.lstrip("/")

    def get_image_url(self, obj):
        if not obj.image_path:
            return None

        normalized_path = self.normalize_image_path(obj.image_path)

        if not normalized_path:
            return None

        if normalized_path.startswith("http://") or normalized_path.startswith("https://"):
            return normalized_path

        url = f"{settings.MEDIA_URL.rstrip('/')}/{normalized_path}"

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(url)

        return url


class ConfigurationSerializer(serializers.ModelSerializer):
    drive_type = serializers.SerializerMethodField()
    fuel_type = serializers.SerializerMethodField()
    engine_model = serializers.SerializerMethodField()
    transmission = serializers.SerializerMethodField()
    seats_count = serializers.SerializerMethodField()
    engine_power_kw = serializers.SerializerMethodField()
    engine_power_hp = serializers.SerializerMethodField()
    turbo_present = serializers.SerializerMethodField()
    front_tires = serializers.SerializerMethodField()
    rear_tires = serializers.SerializerMethodField()
    body_type = serializers.SerializerMethodField()
    body_mark = serializers.SerializerMethodField()
    manufacture_year = serializers.SerializerMethodField()

    class Meta:
        model = Configuration
        fields = [
            'id',
            'generation',
            'name',
            'link',
            'engine_name',
            'date_start',
            'date_end',

            # данные из car_data для отображения и выбора комплектации
            'drive_type',
            'fuel_type',
            'engine_model',
            'transmission',
            'seats_count',
            'engine_power_kw',
            'engine_power_hp',
            'turbo_present',
            'front_tires',
            'rear_tires',
            'body_type',
            'body_mark',
            'manufacture_year',
        ]

    def get_car_data(self, obj):
        return CarData.objects.filter(configuration_id=obj.id).first()

    def get_drive_type(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.drive_type if car_data else None

    def get_fuel_type(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.fuel_type if car_data else None

    def get_engine_model(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.engine_model if car_data else None

    def get_transmission(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.transmission if car_data else None

    def get_seats_count(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.seats_count if car_data else None

    def get_engine_power_kw(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.engine_power_kw if car_data else None

    def get_engine_power_hp(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.engine_power_hp if car_data else None

    def get_turbo_present(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.turbo_present if car_data else None

    def get_front_tires(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.front_tires if car_data else None

    def get_rear_tires(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.rear_tires if car_data else None

    def get_body_type(self, obj):
        car_data = self.get_car_data(obj)

        if car_data and car_data.body_type:
            return car_data.body_type

        if obj.generation and obj.generation.body_type:
            return obj.generation.body_type

        return None

    def get_body_mark(self, obj):
        car_data = self.get_car_data(obj)

        if car_data and car_data.body_mark:
            return normalize_body_mark_value(car_data.body_mark)

        return None

    def get_manufacture_year(self, obj):
        car_data = self.get_car_data(obj)
        return car_data.manufacture_year if car_data else None


class CarDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarData
        fields = '__all__'


class CarDataProtocolSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(
        source='configuration.generation.model.brand.name',
        read_only=True
    )
    model_name = serializers.CharField(
        source='configuration.generation.model.name',
        read_only=True
    )
    generation_id = serializers.IntegerField(
        source='configuration.generation.id',
        read_only=True
    )
    generation_name = serializers.CharField(
        source='configuration.generation.name',
        read_only=True
    )
    configuration_id = serializers.IntegerField(
        source='configuration.id',
        read_only=True
    )
    normalized_body_mark = serializers.SerializerMethodField()

    class Meta:
        model = CarData
        fields = [
            'id',
            'configuration_id',
            'brand_name',
            'model_name',
            'generation_id',
            'generation_name',

            'configuration_name',
            'manufacture_year',
            'body_type',
            'body_mark',
            'normalized_body_mark',

            'front_tires',
            'rear_tires',

            'fuel_type',
            'transmission',
            'drive_type',
            'seats_count',
            'clearance',

            'vehicle_weight_kg',

            'engine_model',
            'engine_capacity',
            'engine_power_hp',
            'engine_power_kw',
            'cylinder_layout',
            'cylinders_count',
            'turbo_present',

            'front_brakes',
            'rear_brakes',

            'vehicle_length_mm',
            'vehicle_width_mm',
            'vehicle_height_mm',
        ]

    def get_normalized_body_mark(self, obj):
        return normalize_body_mark_value(obj.body_mark)


# =========================
# Протокол
# =========================

class ProtocolSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    locked_by_username = serializers.CharField(
        source='locked_by.username',
        read_only=True
    )
    locked_by_full_name = serializers.SerializerMethodField()
    cancelled_by_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Protocol
        fields = '__all__'
        read_only_fields = [
            'id',
            'protocol_number',
            'status',
            'user',
            'locked_by',
            'locked_at',
            'cancelled_by',
            'cancelled_at',
            'created_at',
            'updated_at',
        ]

    def validate_status(self, value):
        if value in {'approved', 'cancelled'}:
            raise serializers.ValidationError(
                'Этот статус устанавливается только специальным действием.'
            )

        return value

    def get_locked_by_full_name(self, obj):
        if not obj.locked_by:
            return None

        full_name = f"{obj.locked_by.last_name} {obj.locked_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.locked_by.username

    def get_cancelled_by_full_name(self, obj):
        if not obj.cancelled_by:
            return None

        full_name = f"{obj.cancelled_by.last_name} {obj.cancelled_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.cancelled_by.username


class ProtocolMeasurementSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolMeasurement
        fields = '__all__'
        read_only_fields = ['id']


class ProtocolBrakeSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolBrake
        fields = '__all__'
        read_only_fields = ['id']


class ProtocolLightSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolLight
        fields = '__all__'
        read_only_fields = ['id']


class ProtocolPhotoSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()
    is_docx_photo = serializers.SerializerMethodField()

    class Meta:
        model = ProtocolPhoto
        fields = [
            'id',
            'protocol',
            'photo_type',
            'file_path',
            'file_url',
            'caption',
            'is_docx_photo',
            'sort_order',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'protocol',
            'file_path',
            'file_url',
            'caption',
            'is_docx_photo',
            'created_at',
        ]

    def get_file_url(self, obj):
        if not obj.file_path:
            return None

        request = self.context.get('request')
        url = f"{settings.MEDIA_URL}{obj.file_path}"

        if request:
            return request.build_absolute_uri(url)

        return url

    def get_caption(self, obj):
        captions = {
            'stand_test_photo': 'Фото 1. Испытания на тормозном стенде',
            'gas_test_photo': 'Фото 2. Измерение уровня выбросов отработавших газов',
            'noise_test_photo': 'Фото 3. Измерение уровня шума',
        }

        return captions.get(obj.photo_type, obj.get_photo_type_display())

    def get_is_docx_photo(self, obj):
        return obj.photo_type in [
            'stand_test_photo',
            'gas_test_photo',
            'noise_test_photo',
        ]


class ProtocolTestConditionSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolTestCondition
        fields = '__all__'
        read_only_fields = ['id']


class ProtocolRoadConditionSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolRoadCondition
        fields = '__all__'
        read_only_fields = ['id']


class ProtocolPowerSupplySerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProtocolPowerSupply
        fields = '__all__'
        read_only_fields = ['id']


# =========================
# Полный / детальный протокол
# =========================

class ProtocolDetailSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    locked_by_username = serializers.CharField(
        source='locked_by.username',
        read_only=True
    )

    locked_by_full_name = serializers.SerializerMethodField()
    cancelled_by_full_name = serializers.SerializerMethodField()

    measurement = ProtocolMeasurementSerializer(read_only=True)
    brake = ProtocolBrakeSerializer(read_only=True)
    light = ProtocolLightSerializer(read_only=True)
    test_conditions = ProtocolTestConditionSerializer(read_only=True)
    road_conditions = ProtocolRoadConditionSerializer(read_only=True)
    power_supply = ProtocolPowerSupplySerializer(read_only=True)
    photos = ProtocolPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Protocol
        fields = '__all__'

    def get_locked_by_full_name(self, obj):
        if not obj.locked_by:
            return None

        full_name = f"{obj.locked_by.last_name} {obj.locked_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.locked_by.username

    def get_cancelled_by_full_name(self, obj):
        if not obj.cancelled_by:
            return None

        full_name = f"{obj.cancelled_by.last_name} {obj.cancelled_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.cancelled_by.username


class ProtocolFullSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    locked_by_username = serializers.CharField(
        source='locked_by.username',
        read_only=True
    )

    locked_by_full_name = serializers.SerializerMethodField()
    cancelled_by_full_name = serializers.SerializerMethodField()

    measurement = ProtocolMeasurementSerializer(read_only=True)
    brake = ProtocolBrakeSerializer(read_only=True)
    light = ProtocolLightSerializer(read_only=True)
    test_conditions = ProtocolTestConditionSerializer(read_only=True)
    road_conditions = ProtocolRoadConditionSerializer(read_only=True)
    power_supply = ProtocolPowerSupplySerializer(read_only=True)
    photos = ProtocolPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Protocol
        fields = '__all__'

    def get_locked_by_full_name(self, obj):
        if not obj.locked_by:
            return None

        full_name = f"{obj.locked_by.last_name} {obj.locked_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.locked_by.username

    def get_cancelled_by_full_name(self, obj):
        if not obj.cancelled_by:
            return None

        full_name = f"{obj.cancelled_by.last_name} {obj.cancelled_by.first_name}".strip()

        if full_name:
            return full_name

        return obj.cancelled_by.username


# =========================
# Создание протокола
# =========================

class ProtocolCreateSerializer(DashFieldsSerializerMixin, serializers.ModelSerializer):
    configuration_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Protocol
        fields = [
            'id',
            'configuration_id',

            'protocol_number',
            'protocol_date',
            'status',
            'user',
            'model',
            'car',

            'owner_type',
            'owner_name',
            'owner_last_name',
            'owner_first_name',
            'owner_middle_name',
            'owner_address',
            'owner_document',
            'owner_phone',
            'manufacturer_info',

            'appendix_number',
            'commercial_name',
            'brand_name',
            'vehicle_category',
            'body_type',

            'vin',
            'chassis_number',
            'body_number',
            'engine_number',
            'registration_number',

            'wheel_marking_front',
            'wheel_marking_rear',
            'tire_season',
            'has_spikes',

            'manufacture_year',
            'manufacture_date',
            'color',
            'inspection_place',
            'comment',

            # Список полей верхнего блока Protocol, где пользователь поставил "-"
            'dash_fields',

            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'protocol_number',
            'status',
            'user',
            'created_at',
            'updated_at',
        ]

    def normalize_body_mark(self, value):
        return normalize_body_mark_value(value)

    def normalize_fuel_type(self, value):
        if not value:
            return None

        value = str(value).lower()

        if 'бенз' in value or 'petrol' in value or 'gasoline' in value:
            return 'petrol'
        if 'диз' in value or 'diesel' in value:
            return 'diesel'
        if 'гибрид' in value or 'hybrid' in value:
            return 'hybrid'
        if 'элект' in value or 'electric' in value:
            return 'electric'

        return None

    def normalize_transmission(self, value):
        if not value:
            return None

        value = str(value).lower()

        if 'вариатор' in value or 'cvt' in value:
            return 'variator'
        if 'механ' in value or 'мкпп' in value or 'manual' in value:
            return 'manual'
        if 'робот' in value or 'robot' in value:
            return 'robot'
        if 'редуктор' in value or 'reductor' in value:
            return 'reductor'
        if 'автомат' in value or 'акпп' in value or 'automatic' in value:
            return 'automatic'

        return None

    def normalize_wheel_formula(self, value):
        if not value:
            return None

        value = str(value).lower()

        if 'перед' in value or 'front' in value:
            return '4x2_front'
        if 'зад' in value or 'rear' in value:
            return '4x2_rear'
        if 'полн' in value or '4wd' in value or 'awd' in value or '4x4' in value:
            return '4x4'

        return None

    def normalize_cylinder_layout(self, value):
        if not value:
            return None

        value = str(value).lower()

        if 'ряд' in value or 'inline' in value:
            return 'inline'
        if 'оппозит' in value or 'opposed' in value:
            return 'opposed'
        if 'v' in value or 'v-' in value or 'v образ' in value:
            return 'v_shape'

        return None

    def normalize_service_brake_type(self, front_brakes, rear_brakes):
        front = str(front_brakes or '').lower()
        rear = str(rear_brakes or '').lower()

        front_is_disc = 'диск' in front or 'disc' in front
        rear_is_disc = 'диск' in rear or 'disc' in rear
        rear_is_drum = 'барабан' in rear or 'drum' in rear

        if front_is_disc and rear_is_disc:
            return 'disc_disc'

        if front_is_disc and rear_is_drum:
            return 'disc_drum'

        return None

    def get_default_light_values(self):
        """
        Дефолтные значения под актуальный шаблон протокола.
        Пользователь потом может изменить их на странице осмотра.
        """
        return {
            'low_beam_count': 2,
            'low_beam_color': 'белый',

            'high_beam_count': 2,
            'high_beam_color': 'белый',

            'turn_signal_count': 2,
            'turn_signal_color': 'автожелтый',

            'front_position_light_count': 2,
            'front_position_light_color': 'белый',

            'rear_position_light_count': 2,
            'rear_position_light_color': 'красный',

            'main_brake_signal_count': 2,
            'main_brake_signal_color': 'красный',

            'rear_parking_light_count': None,
            'rear_parking_light_color': 'красный',

            'parking_light_count': None,
            'parking_light_color': 'белый',

            'front_fog_count': None,
            'front_fog_color': 'белый',

            'reverse_light_count': None,
            'reverse_light_color': 'белый',

            'additional_brake_signal_count': None,
            'additional_brake_signal_color': 'красный',

            'rear_fog_count': None,
            'rear_fog_color': 'красный',

            'plate_light_count': None,
            'plate_light_color': 'белый',

            'daytime_running_light_count': None,
            'daytime_running_light_color': 'белый',

            'adaptive_front_lighting_count': None,
            'adaptive_front_lighting_color': 'белый',
        }

    def create(self, validated_data):
        configuration_id = validated_data.pop('configuration_id', None)

        car_data = None
        configuration = None

        if configuration_id:
            car_data = (
                CarData.objects
                .select_related(
                    'configuration',
                    'configuration__generation',
                    'configuration__generation__model',
                    'configuration__generation__model__brand',
                )
                .filter(configuration_id=configuration_id)
                .first()
            )

            if not car_data:
                raise serializers.ValidationError({
                    'configuration_id': 'Для выбранной комплектации не найдены данные car_data'
                })

            configuration = car_data.configuration
            generation = configuration.generation
            model = generation.model
            brand = model.brand

            validated_data['car'] = car_data

            if not validated_data.get('brand_name'):
                validated_data['brand_name'] = brand.name

            if not validated_data.get('commercial_name'):
                validated_data['commercial_name'] = model.name

            normalized_body_mark = self.normalize_body_mark(car_data.body_mark)

            if normalized_body_mark:
                validated_data['body_type'] = normalized_body_mark
            elif not validated_data.get('body_type'):
                validated_data['body_type'] = car_data.body_type or generation.body_type

            if not validated_data.get('wheel_marking_front'):
                validated_data['wheel_marking_front'] = car_data.front_tires

            if not validated_data.get('wheel_marking_rear'):
                validated_data['wheel_marking_rear'] = car_data.rear_tires

            if not validated_data.get('manufacture_year'):
                validated_data['manufacture_year'] = car_data.manufacture_year

        if not validated_data.get('protocol_number'):
            validated_data['protocol_number'] = f"TEMP-{uuid4().hex[:12]}"

        protocol = Protocol.objects.create(**validated_data)

        protocol.protocol_number = str(protocol.id).zfill(5)

        if not protocol.appendix_number:
            protocol.appendix_number = protocol.protocol_number

        protocol.save(update_fields=['protocol_number', 'appendix_number'])

        measurement_defaults = {}

        if car_data:
            measurement_defaults = {
                'wheel_formula': self.normalize_wheel_formula(car_data.drive_type),
                'seats_count': car_data.seats_count,

                'engine_model': car_data.engine_model or configuration.engine_name,
                'engine_power_kw': car_data.engine_power_kw,
                'fuel_type': self.normalize_fuel_type(car_data.fuel_type),
                'cylinder_layout': self.normalize_cylinder_layout(car_data.cylinder_layout),
                'cylinders_count': car_data.cylinders_count,
                'turbo_present': car_data.turbo_present,

                'transmission_type': self.normalize_transmission(car_data.transmission),

                'vehicle_length_mm': car_data.vehicle_length_mm,
                'vehicle_width_mm': car_data.vehicle_width_mm,
                'vehicle_height_mm': car_data.vehicle_height_mm,
                'vehicle_weight_kg': car_data.vehicle_weight_kg,
            }

        ProtocolMeasurement.objects.create(
            protocol=protocol,
            **measurement_defaults
        )

        brake_defaults = {}

        if car_data:
            service_brake_type = self.normalize_service_brake_type(
                car_data.front_brakes,
                car_data.rear_brakes
            )

            if service_brake_type:
                brake_defaults['service_brake_type'] = service_brake_type

        ProtocolBrake.objects.create(
            protocol=protocol,
            **brake_defaults
        )

        ProtocolLight.objects.create(
            protocol=protocol,
            **self.get_default_light_values()
        )

        ProtocolTestCondition.objects.create(protocol=protocol)
        ProtocolRoadCondition.objects.create(protocol=protocol)
        ProtocolPowerSupply.objects.create(protocol=protocol)

        return protocol


# =========================
# Пользователь
# =========================
USER_ROLE_CHOICES = [
    ('measurer', 'Замерщик'),
    ('operator', 'Оформитель'),
    ('manager', 'Руководитель'),
    ('executive_director', 'Исполнительный директор'),
]

USER_ROLE_LABELS = dict(USER_ROLE_CHOICES)


def ensure_user_role_groups():
    for role_value, role_label in USER_ROLE_CHOICES:
        Group.objects.get_or_create(
            name=role_value
        )


def get_user_role(user):
    if user.is_superuser:
        return 'superuser'

    role_names = set(user.groups.values_list('name', flat=True))

    for role_value, _role_label in USER_ROLE_CHOICES:
        if role_value in role_names:
            return role_value

    return None


def get_user_role_label(user):
    if user.is_superuser:
        return 'Суперпользователь'

    role = get_user_role(user)

    if not role:
        return 'Без роли'

    return USER_ROLE_LABELS.get(role, role)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'role',
            'role_label',
        ]
        read_only_fields = [
            'id',
            'is_staff',
            'is_superuser',
            'date_joined',
            'role',
            'role_label',
        ]

    def get_role(self, obj):
        return get_user_role(obj)

    def get_role_label(self, obj):
        return get_user_role_label(obj)


class CreateUserSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True
    )
    password = serializers.CharField(
        min_length=4,
        required=True,
        write_only=True
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )
    role = serializers.ChoiceField(
        choices=USER_ROLE_CHOICES,
        required=True
    )

    def validate_username(self, value):
        username = value.strip()

        if not username:
            raise serializers.ValidationError('Логин не может быть пустым')

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Пользователь с таким логином уже существует')

        return username

    def create(self, validated_data):
        ensure_user_role_groups()

        password = validated_data.pop('password')
        role = validated_data.pop('role')

        user = User.objects.create_user(
            username=validated_data.get('username'),
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )

        group = Group.objects.get(name=role)
        user.groups.add(group)

        return user


class UpdateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True
    )
    role = serializers.ChoiceField(
        choices=USER_ROLE_CHOICES,
        required=True
    )
    new_password = serializers.CharField(
        min_length=4,
        required=False,
        allow_blank=True,
        write_only=True
    )
    current_password = serializers.CharField(
        required=True,
        write_only=True
    )

    def validate_current_password(self, value):
        request = self.context.get("request")

        if not request or not request.user:
            raise serializers.ValidationError("Не удалось определить текущего пользователя")

        if not request.user.check_password(value):
            raise serializers.ValidationError("Неверный пароль текущего пользователя")

        return value

    def update(self, instance, validated_data):
        ensure_user_role_groups()

        validated_data.pop("current_password", None)

        new_password = validated_data.pop("new_password", "")
        role = validated_data.pop("role")

        instance.first_name = validated_data.get("first_name", "")
        instance.last_name = validated_data.get("last_name", "")
        instance.email = validated_data.get("email", "")

        if new_password:
            instance.set_password(new_password)

        instance.save()

        instance.groups.clear()
        group = Group.objects.get(name=role)
        instance.groups.add(group)

        return instance
