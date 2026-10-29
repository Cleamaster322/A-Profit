import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import {renderField, renderSelect} from "./protocolInspectionHelpers.jsx";
import {isElectricVehicle} from "./electricVehicleFields.js";

function ProtocolInspectionEngine({
                                      form,
                                      handleChange,
                                      measurementMode = false,
                                      textFieldSx,
                                      selectFieldSx,
                                      sectionPaperSx,
                                      sectionTitleSx,
                                      subsectionTitleSx,
                                  }) {
    // У электромобиля нет ДВС: расположение, цилиндры и нагнетатель скрываем.
    const electric = isElectricVehicle(form);

    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                5. Двигатель
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Основные параметры двигателя
            </Typography>

            <Grid container spacing={2} sx={{mb: 2}}>
                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Модель двигателя",
                    name: "engine_model",
                    md: 6,
                })}

                {!measurementMode && renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Мощность двигателя, кВт",
                    name: "engine_power_kw",
                    md: 6,
                })}
            </Grid>

            {!electric && <Grid container spacing={2} sx={{mb: 2}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Расположение двигателя",
                    name: "engine_layout",
                    md: 6,
                    options: [
                        {value: "transverse", label: "Поперечное"},
                        {value: "longitudinal", label: "Продольное"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Расположение цилиндров",
                    name: "cylinder_layout",
                    md: 6,
                    options: [
                        {value: "inline", label: "Рядное"},
                        {value: "opposed", label: "Оппозитное"},
                        {value: "v_shape", label: "V-образное"},
                    ],
                })}
            </Grid>}

            <Grid container spacing={2}>
                {!electric && renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Количество цилиндров",
                    name: "cylinders_count",
                    md: 4,
                    options: [
                        {value: "3", label: "3"},
                        {value: "4", label: "4"},
                        {value: "6", label: "6"},
                        {value: "8", label: "8"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Вид топлива",
                    name: "fuel_type",
                    md: 4,
                    options: [
                        {value: "petrol", label: "Бензин"},
                        {value: "diesel", label: "Дизель"},
                        {value: "hybrid_petrol", label: "Гибрид-бензин"},
                        {value: "hybrid_diesel", label: "Гибрид-дизель"},
                        {value: "electric", label: "Электро"},
                    ],
                })}

                {!electric && renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Нагнетатель",
                    name: "supercharger",
                    md: 4,
                    options: [
                        {value: "absent", label: "Отсутствует"},
                        {value: "compressor", label: "Компрессор"},
                        {value: "turbo", label: "Турбина"},
                        {value: "twin_turbo", label: "Твин-турбо"},
                    ],
                })}
            </Grid>
        </Paper>
    );
}

export default ProtocolInspectionEngine;