import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import {renderField, renderSelect} from "./protocolInspectionHelpers.jsx";

function ProtocolInspectionVehicle({
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
                4. Основные сведения об автомобиле
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Идентификация и общие сведения
            </Typography>

            <Grid container spacing={2} sx={{mb: 2}}>
                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Марка",
                    name: "brand_name",
                    md: 3,
                    placeholder: "Nissan",
                })}

                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Коммерческое название",
                    name: "commercial_name",
                    md: 3,
                    placeholder: "DAYZ",
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "VIN / № кузова / № шасси",
                    name: "vin",
                    md: 3,
                    placeholder: "B43W-0105450",
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Категория",
                    name: "category",
                    md: 3,
                    options: [
                        {value: "M1", label: "M1"},
                        {value: "N1", label: "N1"},
                    ],
                })}
            </Grid>

            <Grid container spacing={2} sx={{mb: 2}}>
                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Тип / код кузова",
                    name: "body_type",
                    md: 4,
                    placeholder: "B43W",
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Пробег, км",
                    name: "mileage_km",
                    md: measurementMode ? 12 : 4,
                    placeholder: "35000",
                })}

                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Год выпуска",
                    name: "manufacture_year",
                    md: 4,
                    placeholder: "2023",
                })}
            </Grid>

            <Grid container spacing={2} sx={{mb: 2}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Маркировка колес / шин передней оси",
                    name: "tire_marking_front",
                    md: 6,
                    placeholder: "155/65R14",
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Маркировка колес / шин задней оси",
                    name: "tire_marking_rear",
                    md: 6,
                    placeholder: "155/65R14",
                })}
            </Grid>

            <Grid container spacing={2} sx={{mb: 2}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Сезонность шин",
                    name: "tire_season",
                    md: 4,
                    options: [
                        {value: "summer", label: "Лето"},
                        {value: "winter", label: "Зима"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Наличие шипов",
                    name: "tire_spikes_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Да"},
                        {value: "false", label: "Нет"},
                    ],
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Цвет",
                    name: "color",
                    md: 4,
                })}
            </Grid>

            <Grid container spacing={2} sx={{mb: 2}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Колесная формула",
                    name: "wheel_formula",
                    md: 4,
                    options: [
                        {value: "4x2_front", label: "4х2 передний"},
                        {value: "4x2_rear", label: "4х2 задний"},
                        {value: "4x4", label: "4х4 полный"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Количество глушителей",
                    name: "mufflers_count",
                    md: 4,
                    options: [
                        {value: "1", label: "1"},
                        {value: "2", label: "2"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Подножки",
                    name: "side_steps_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Наличие"},
                        {value: "false", label: "Отсутствие"},
                    ],
                })}
            </Grid>

            <Grid container spacing={2}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Количество посадочных мест",
                    name: "seats_count",
                    md: 12,
                    placeholder: "2/2 или 2/3",
                })}
            </Grid>
        </Paper>
    );
}

export default ProtocolInspectionVehicle;