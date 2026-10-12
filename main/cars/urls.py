from django.urls import path
from .views import (
    create_employee_user,
    create_protocol,
    create_protocol_brake,
    create_protocol_light,
    create_protocol_measurement,
    create_protocol_photo,
    create_protocol_power_supply,
    create_protocol_road_conditions,
    create_protocol_test_conditions,
    create_word,
    delete_car_data,
    delete_brand,
    delete_configuration,
    delete_employee_user,
    delete_generation,
    delete_model,
    delete_protocol,
    delete_protocol_photo,
    get_all_brands,
    get_all_car_data,
    get_all_configurations,
    get_all_generations,
    get_all_models,
    get_all_protocols,
    get_all_users,
    get_brand,
    get_car_data,
    get_car_data_by_configuration,
    get_configuration,
    get_configuration_filter_options,
    get_csrf_token,
    get_filtered_configurations,
    get_filtered_generations,
    get_full_protocol,
    get_generation,
    get_model,
    get_model_filter_options,
    get_protocol,
    get_protocol_brake,
    get_protocol_light,
    get_protocol_measurement,
    get_protocol_photos,
    get_protocol_power_supply,
    get_protocol_road_conditions,
    get_protocol_test_conditions,
    get_user,
    logout,
    manager_release_protocol_lock,
    protocol_access_required,
    protocol_heartbeat,
    post_brand,
    post_car_data,
    post_configuration,
    post_generation,
    post_model,
    return_protocol_to_draft,
    submit_protocol_for_review,
    submit_protocol_to_operator,
    select_protocol_configuration,
    start_protocol_editing,
    update_car_data,
    update_brand,
    update_configuration,
    update_employee_user,
    update_generation,
    update_model,
    update_protocol,
    update_protocol_brake,
    update_protocol_light,
    update_protocol_measurement,
    update_protocol_photo,
    update_protocol_power_supply,
    update_protocol_road_conditions,
    update_protocol_test_conditions,
    approve_protocol,
    cancel_protocol,
    generate_protocol_docx_file,
    preview_protocol_pdf_file,
)

urlpatterns = [
    # --- CSRF ---
    path('get_csrf_token/', get_csrf_token),
    path('logout/', logout),

    # =========================================================
    # --- BRANDS ---
    # =========================================================
    path('brands/', get_all_brands),
    path('brands/<int:pk>/', get_brand),
    path('brands/create/', post_brand),
    path('brands/<int:pk>/update/', update_brand),
    path('brands/<int:pk>/delete/', delete_brand),

    # =========================================================
    # --- MODELS ---
    # =========================================================
    path('models/', get_all_models),
    path('models/<int:pk>/', get_model),
    path('models/create/', post_model),
    path('models/<int:pk>/update/', update_model),
    path('models/<int:pk>/delete/', delete_model),

    # =========================================================
    # --- GENERATIONS ---
    # =========================================================
    path('generations/', get_all_generations),
    path('generations/<int:pk>/', get_generation),
    path('generations/create/', post_generation),
    path('generations/<int:pk>/update/', update_generation),
    path('generations/<int:pk>/delete/', delete_generation),
    path('model-filter-options/', get_model_filter_options),
    path('generations-filtered/', get_filtered_generations),

    # =========================================================
    # --- CONFIGURATIONS ---
    # =========================================================
    path('configurations/', get_all_configurations),
    path('configurations/<int:pk>/', get_configuration),
    path('configurations/create/', post_configuration),
    path('configurations/<int:pk>/update/', update_configuration),
    path('configurations/<int:pk>/delete/', delete_configuration),
    path('configuration-filter-options/', get_configuration_filter_options),
    path('configurations-filtered/', get_filtered_configurations),

    # =========================================================
    # --- CAR DATA ---
    # =========================================================
    path('car-data/', get_all_car_data),
    path('car-data/<int:pk>/', get_car_data),
    path('configurations/<int:configuration_id>/car-data/', get_car_data_by_configuration),
    path('car-data/create/', post_car_data),
    path('car-data/<int:pk>/update/', update_car_data),
    path('car-data/<int:pk>/delete/', delete_car_data),

    # =========================================================
    # --- PROTOCOLS ---
    # =========================================================
    path('protocols/', get_all_protocols),
    path('protocols/create/', create_protocol),
    path('protocols/<int:pk>/', protocol_access_required(get_protocol)),
    path('protocols/<int:pk>/update/', protocol_access_required(update_protocol)),

    path('protocols/<int:pk>/start-editing/', protocol_access_required(start_protocol_editing)),
    path('protocols/<int:pk>/heartbeat/', protocol_access_required(protocol_heartbeat)),
    path('protocols/<int:pk>/return-to-draft/', protocol_access_required(return_protocol_to_draft)),
    path('protocols/<int:pk>/submit-to-operator/', protocol_access_required(submit_protocol_to_operator)),
    path('protocols/<int:pk>/submit-for-review/', protocol_access_required(submit_protocol_for_review)),
    path('protocols/<int:pk>/select-configuration/', protocol_access_required(select_protocol_configuration)),
    path('protocols/<int:pk>/manager-release-lock/', protocol_access_required(manager_release_protocol_lock)),
    path('protocols/<int:pk>/approve/', protocol_access_required(approve_protocol)),
    path('protocols/<int:pk>/cancel/', protocol_access_required(cancel_protocol)),

    path('protocols/<int:pk>/delete/', protocol_access_required(delete_protocol)),
    path('protocols/<int:protocol_id>/full/', protocol_access_required(get_full_protocol)),
    path('protocols/<int:protocol_id>/generate-docx/', protocol_access_required(generate_protocol_docx_file)),
    path('protocols/<int:protocol_id>/preview-pdf/', protocol_access_required(preview_protocol_pdf_file)),

    # =========================================================
    # --- MEASUREMENT ---
    # =========================================================
    path('protocols/<int:protocol_id>/measurement/', protocol_access_required(get_protocol_measurement)),
    path('protocols/<int:protocol_id>/measurement/create/', protocol_access_required(create_protocol_measurement)),
    path('protocols/<int:protocol_id>/measurement/update/', protocol_access_required(update_protocol_measurement)),

    # =========================================================
    # --- BRAKE ---
    # =========================================================
    path('protocols/<int:protocol_id>/brake/', protocol_access_required(get_protocol_brake)),
    path('protocols/<int:protocol_id>/brake/create/', protocol_access_required(create_protocol_brake)),
    path('protocols/<int:protocol_id>/brake/update/', protocol_access_required(update_protocol_brake)),

    # =========================================================
    # --- LIGHT ---
    # =========================================================
    path('protocols/<int:protocol_id>/light/', protocol_access_required(get_protocol_light)),
    path('protocols/<int:protocol_id>/light/create/', protocol_access_required(create_protocol_light)),
    path('protocols/<int:protocol_id>/light/update/', protocol_access_required(update_protocol_light)),

    # =========================================================
    # --- TEST CONDITIONS ---
    # =========================================================
    path('protocols/<int:protocol_id>/test-conditions/', protocol_access_required(get_protocol_test_conditions)),
    path('protocols/<int:protocol_id>/test-conditions/create/', protocol_access_required(create_protocol_test_conditions)),
    path('protocols/<int:protocol_id>/test-conditions/update/', protocol_access_required(update_protocol_test_conditions)),

    # =========================================================
    # --- ROAD CONDITIONS ---
    # =========================================================
    path('protocols/<int:protocol_id>/road-conditions/', protocol_access_required(get_protocol_road_conditions)),
    path('protocols/<int:protocol_id>/road-conditions/create/', protocol_access_required(create_protocol_road_conditions)),
    path('protocols/<int:protocol_id>/road-conditions/update/', protocol_access_required(update_protocol_road_conditions)),

    # =========================================================
    # --- POWER SUPPLY ---
    # =========================================================
    path('protocols/<int:protocol_id>/power-supply/', protocol_access_required(get_protocol_power_supply)),
    path('protocols/<int:protocol_id>/power-supply/create/', protocol_access_required(create_protocol_power_supply)),
    path('protocols/<int:protocol_id>/power-supply/update/', protocol_access_required(update_protocol_power_supply)),

    # =========================================================
    # --- PHOTOS ---
    # =========================================================
    path('protocols/<int:protocol_id>/photos/', protocol_access_required(get_protocol_photos)),
    path('protocols/<int:protocol_id>/photos/create/', protocol_access_required(create_protocol_photo)),
    path('protocol-photos/<int:photo_id>/update/', protocol_access_required(update_protocol_photo)),
    path('protocol-photos/<int:photo_id>/delete/', protocol_access_required(delete_protocol_photo)),

    # =========================================================
    # --- USERS ---
    # =========================================================
    path('get-all-users/', get_all_users),
    path('get-user/', get_user),
    path('users/create/', create_employee_user),
    path('users/<int:user_id>/update/', update_employee_user),
    path('users/<int:user_id>/delete/', delete_employee_user),

    # =========================================================
    # --- WORD DOCUMENTS ---
    # =========================================================
    path('create-word/', create_word),
]
