import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import {renderField} from "./protocolInspectionHelpers.jsx";

function ProtocolInspectionLightsGeometry({
                                              form,
                                              handleChange,
                                              textFieldSx,
                                              sectionPaperSx,
                                              sectionTitleSx,
                                              subsectionTitleSx,
                                          }) {
    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                9. Геометрия установки световых приборов
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Установка фар ближнего света по высоте
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Верхняя точка, мм",
                    name: "low_beam_upper_point_mm",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Нижняя точка, мм",
                    name: "low_beam_lower_point_mm",
                    md: 6,
                })}
            </Grid>

            {Number(form.front_fog_count) > 0 && (
                <>
                    <Typography variant="h6" sx={subsectionTitleSx}>
                        Установка ПТФ по высоте
                    </Typography>

                    <Grid container spacing={2} sx={{mb: 3}}>
                        {renderField({
                            form,
                            handleChange,
                            textFieldSx,
                            label: "Верхняя точка, мм",
                            name: "fog_light_upper_point_mm",
                            md: 6,
                        })}

                        {renderField({
                            form,
                            handleChange,
                            textFieldSx,
                            label: "Нижняя точка, мм",
                            name: "fog_light_lower_point_mm",
                            md: 6,
                        })}
                    </Grid>

                    <Typography variant="h6" sx={subsectionTitleSx}>
                        Установка ПТФ по ширине
                    </Typography>

                    <Grid container spacing={2} sx={{mb: 3}}>
                        {renderField({
                            form,
                            handleChange,
                            textFieldSx,
                            label: "Левая и правая, мм",
                            name: "fog_light_left_distance_mm",
                            md: 12,
                        })}
                    </Grid>
                </>
            )}

            <Typography variant="h6" sx={subsectionTitleSx}>
                Установка основных сигналов торможения по высоте
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Верхняя точка, мм",
                    name: "brake_signal_upper_point_mm",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Нижняя точка, мм",
                    name: "brake_signal_lower_point_mm",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Установка основных сигналов торможения по ширине
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Левая и правая, мм",
                    name: "brake_signal_left_distance_mm",
                    md: 12,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Установка дополнительного сигнала торможения
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "От нижнего края покрытия заднего стекла, мм",
                    name: "additional_brake_signal_from_glass_edge_mm",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "От уровня опорной поверхности, мм",
                    name: "additional_brake_signal_from_support_surface_mm",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Смещение оптического центра, мм",
                    name: "additional_brake_signal_optical_center_shift_mm",
                    md: 4,
                })}
            </Grid>

            {Number(form.rear_fog_count) > 0 && (
                <>
                    <Typography variant="h6" sx={subsectionTitleSx}>
                        Установка задних ПТФ по высоте
                    </Typography>

                    <Grid container spacing={2}>
                        {renderField({
                            form,
                            handleChange,
                            textFieldSx,
                            label: "Верхняя точка, мм",
                            name: "rear_fog_upper_point_mm",
                            md: 6,
                        })}

                        {renderField({
                            form,
                            handleChange,
                            textFieldSx,
                            label: "Нижняя точка, мм",
                            name: "rear_fog_lower_point_mm",
                            md: 6,
                        })}
                    </Grid>
                </>
            )}
        </Paper>
    );
}

export default ProtocolInspectionLightsGeometry;