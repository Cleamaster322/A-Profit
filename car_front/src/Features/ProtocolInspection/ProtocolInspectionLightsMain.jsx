import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Divider from "@mui/material/Divider";
import {renderField, renderSelect, renderLightPair} from "./protocolInspectionHelpers.jsx";

function ProtocolInspectionLightsMain({
                                          form,
                                          handleChange,
                                          textFieldSx,
                                          selectFieldSx,
                                          sectionPaperSx,
                                          sectionTitleSx,
                                          subsectionTitleSx,
                                      }) {
    const lightPairs = [
        ["Фара дальнего света", "high_beam_count", "high_beam_color", [2, 4]],
        ["Передняя ПТФ", "front_fog_count", "front_fog_color", [2]],
        ["Фонарь заднего хода", "reverse_light_count", "reverse_light_color", [1, 2]],
        ["Сигнал торможения дополнительный", "additional_brake_signal_count", "additional_brake_signal_color", [1, 2]],
        ["Задний ПТФ", "rear_fog_count", "rear_fog_color", [1, 2]],
        ["Подсветка госномера", "plate_light_count", "plate_light_color", [1, 2]],
        ["ДХО", "daytime_running_light_count", "daytime_running_light_color", [2]],
        ["Стояночные огни передние", "parking_light_count", "parking_light_color", [2]],
        ["Стояночные огни задние", "rear_parking_light_count", "rear_parking_light_color", [2]],
        ["Адаптивная система переднего освещения", "adaptive_front_lighting_count", "adaptive_front_lighting_color", [2]],
    ];

    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                8. Осветительные приборы
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Внешние световые приборы
            </Typography>

            {lightPairs.map(([title, countName, colorName, countOptions]) =>
                renderLightPair({
                    form,
                    handleChange,
                    textFieldSx,
                    title,
                    countName,
                    colorName,
                    countOptions,
                    showColor: colorName === "front_fog_color",
                })
            )}

            <Divider sx={{my: 3}}/>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Основные параметры освещения
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Омыватели фар",
                    name: "headlight_washer_present",
                    md: 4,
                    options: [
                        {value: "true", label: "Наличие"},
                        {value: "false", label: "Отсутствие"},
                    ],
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Сила света фар
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левая 34В, кд",
                    name: "left_34v_cd",
                    md: 2,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левая 52Н, кд",
                    name: "left_52h_cd",
                    md: 2,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левая дальний, кд",
                    name: "left_high_beam_cd",
                    md: 2,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правая 34В, кд",
                    name: "right_34v_cd",
                    md: 2,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правая 52Н, кд",
                    name: "right_52h_cd",
                    md: 2,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Правая дальний, кд",
                    name: "right_high_beam_cd",
                    md: 2,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Частота мерцания указателей поворота / аварийной сигнализации
            </Typography>

            <Grid container spacing={2}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Пр./мин.",
                    name: "turn_signal_frequency_per_min",
                    md: 6,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Гц",
                    name: "turn_signal_frequency_hz",
                    md: 6,
                })}
            </Grid>
        </Paper>
    );
}

export default ProtocolInspectionLightsMain;