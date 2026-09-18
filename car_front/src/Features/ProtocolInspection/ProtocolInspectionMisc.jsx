import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import {renderField, renderSelect} from "./protocolInspectionHelpers.jsx";

function ProtocolInspectionMisc({
                                    form,
                                    handleChange,
    measurementMode = false,
                                    textFieldSx,
                                    selectFieldSx,
                                    sectionPaperSx,
                                    sectionTitleSx,
                                    subsectionTitleSx,
                                }) {
    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                10. Прочее
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Комплектность и противоугонное устройство
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Запасное колесо",
                    name: "spare_wheel_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Есть"},
                        {value: "false", label: "Нет"},
                    ],
                })}
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Блокировка рулевого управления",
                    name: "steering_lock_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Есть"},
                        {value: "false", label: "Нет"},
                    ],
                })}
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Кнопка ГЛОНАСС",
                    name: "glonass_button_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Имеется"},
                        {value: "false", label: "Отсутствует"},
                    ],
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Остаточная глубина рисунка протектора
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левое переднее, мм",
                    name: "tire_depth_fl_mm",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правое переднее, мм",
                    name: "tire_depth_fr_mm",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левое заднее, мм",
                    name: "tire_depth_rl_mm",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правое заднее, мм",
                    name: "tire_depth_rr_mm",
                    md: 3,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Кузов
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Расстояние между краем бампера и кузовом, мм",
                    name: "bumper_to_body_distance_mm",
                    md: 6,
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Открывающаяся крыша",
                    name: "opening_roof_present",
                    md: 6,
                    options: [
                        {value: "true", label: "Да"},
                        {value: "false", label: "Нет"},
                    ],
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Выступающие элементы
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ручки дверей, багажника, мм",
                    name: "protruding_elements_doors_mm",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Остальные элементы, мм",
                    name: "protruding_elements_other_mm",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Светопропускание стекол
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правое, %",
                    name: "glass_transparency_right_pct",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левое, %",
                    name: "glass_transparency_left_pct",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ветровое, %",
                    name: "glass_transparency_windshield_pct",
                    md: 4,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Дополнительные параметры
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ширина светозащитной полосы, мм",
                    name: "sun_strip_width_mm",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Суммарный люфт в Р/У, °",
                    name: "steering_backlash_deg",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Скорость транспортного средства
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "По спидометру, км/ч",
                    name: "speed_by_speedometer_kmh",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Фактическая, км/ч",
                    name: "actual_speed_kmh",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Экология и шум
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Шум на повышенных оборотах, дБА",
                    name: "exhaust_noise_constant_db",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Шум в режиме замедления, дБА",
                    name: "exhaust_noise_deceleration_db",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Min обороты: CO, %",
                    name: "co_min_pct",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Max обороты: CO, %",
                    name: "co_max_pct",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Коэффициент поглощения света
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 1, м-1",
                    name: "light_absorption_1",
                    md: 2,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 2, м-1",
                    name: "light_absorption_2",
                    md: 2,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 3, м-1",
                    name: "light_absorption_3",
                    md: 2,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 4, м-1",
                    name: "light_absorption_4",
                    md: 2,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 5, м-1",
                    name: "light_absorption_5",
                    md: 2,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Значение 6, м-1",
                    name: "light_absorption_6",
                    md: 2,
                })}
            </Grid>

            {!measurementMode && <Typography variant="h6" sx={subsectionTitleSx}>
                Габаритные размеры ТС
            </Typography>}

            {!measurementMode && <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Длина, мм",
                    name: "vehicle_length_mm",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ширина, мм",
                    name: "vehicle_width_mm",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Высота, мм",
                    name: "vehicle_height_mm",
                    md: 4,
                })}
            </Grid>}

            {!measurementMode && <Typography variant="h6" sx={subsectionTitleSx}>
                Масса и нагрузка на ось
            </Typography>}

            {!measurementMode && <Grid container spacing={2}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Масса, кг",
                    name: "vehicle_weight_kg",
                    md: 4,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ось 1, кг",
                    name: "axle1_load_kg",
                    md: 4,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ось 2, кг",
                    name: "axle2_load_kg",
                    md: 4,
                })}
            </Grid>}
        </Paper>
    );
}

export default ProtocolInspectionMisc;