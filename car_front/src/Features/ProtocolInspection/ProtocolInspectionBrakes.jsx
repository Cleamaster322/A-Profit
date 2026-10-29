import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import {renderField, renderSelect} from "./protocolInspectionHelpers.jsx";
import {calculateBrakeMetrics, formatMassKg, getDromMassComparisonError} from "./brakeCalculations.js";

function formatMetric(value) {
    return value === null ? "—" : value.toFixed(2).replace(".", ",");
}

function ProtocolInspectionBrakes({
                                      form,
                                      handleChange,
                                      textFieldSx,
                                      selectFieldSx,
                                      sectionPaperSx,
                                      sectionTitleSx,
                                      subsectionTitleSx,
                                      dromMassKg,
                                      measurementMode = false,
                                  }) {
    const metrics = calculateBrakeMetrics(form, dromMassKg);
    const dromMassError = getDromMassComparisonError(form, dromMassKg);
    const metricRows = [
        {
            label: "Удельная тормозная сила рабочей тормозной системы",
            value: metrics.serviceSpecificForce,
            min: 0.52,
            max: 0.98,
            unit: "",
        },
        {
            label: "Удельная тормозная сила стояночной тормозной системы",
            value: metrics.parkingSpecificForce,
            min: 0.18,
            max: 0.48,
            unit: "",
        },
        {
            label: "Относительная разность тормозных сил колес 1-й оси",
            value: metrics.axle1DifferencePct,
            min: 0,
            max: 14,
            unit: "%",
        },
        {
            label: "Относительная разность тормозных сил колес 2-й оси",
            value: metrics.axle2DifferencePct,
            min: 0,
            max: 14,
            unit: "%",
        },
    ];

    return (
        <Paper sx={sectionPaperSx}>
            <Typography variant="h5" sx={sectionTitleSx}>
                7. Тормозная система
            </Typography>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Типы систем
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Рабочая тормозная система",
                    name: "service_brake_type",
                    md: 6,
                    options: [
                        {value: "disc_disc", label: "Дисковая/дисковая"},
                        {value: "disc_drum", label: "Дисковая/барабанная"},
                    ],
                })}

                {renderSelect({
                    form,
                    handleChange,
                    selectFieldSx,
                    label: "Стояночная тормозная система",
                    name: "parking_brake_type",
                    md: 6,
                    options: [
                        {value: "mechanical_hand", label: "Механический ручной"},
                        {value: "mechanical_pedal", label: "Механический педаль"},
                        {value: "electric", label: "Электрический"},
                    ],
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Усилие на органе управления
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Рабочая тормозная система — ось 1, Н",
                    name: "service_brake_control_force_axle1_n",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Рабочая тормозная система — ось 2, Н",
                    name: "service_brake_control_force_axle2_n",
                    md: 4,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Стояночная тормозная система, Н",
                    name: "parking_brake_control_force_n",
                    md: 4,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Тормозная сила рабочей тормозной системы
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Переднее левое, кН",
                    name: "service_brake_front_left_kn",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Переднее правое, кН",
                    name: "service_brake_front_right_kn",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Заднее левое, кН",
                    name: "service_brake_rear_left_kn",
                    md: 3,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Заднее правое, кН",
                    name: "service_brake_rear_right_kn",
                    md: 3,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Тормозная сила стояночной тормозной системы
            </Typography>

            <Grid container spacing={2} sx={{mb: 3}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Заднее левое, кН",
                    name: "parking_brake_left_kn",
                    md: 6,
                })}

                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Заднее правое, кН",
                    name: "parking_brake_right_kn",
                    md: 6,
                })}
            </Grid>

            <Typography variant="h6" sx={subsectionTitleSx}>
                Масса и нагрузка на ось
            </Typography>
            <Grid container spacing={2} sx={{mb: 2}}>
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ось 1, кг",
                    name: "axle1_load_kg",
                    md: 6,
                })}
                {renderField({
                    form,
                    handleChange,
                    textFieldSx,
                    label: "Ось 2, кг",
                    name: "axle2_load_kg",
                    md: 6,
                })}
            </Grid>
            {/* Массы нужны оператору: у замерщика их нет. */}
            {!measurementMode && (
                <Grid container spacing={2} sx={{mb: 3}}>
                    <Grid size={{xs: 12, md: 4}}>
                        <TextField
                            id="drom_vehicle_weight_kg"
                            label="Масса Drom, кг"
                            value={metrics.dromMassKg === null ? "Нет массы Drom" : formatMetric(metrics.dromMassKg)}
                            fullWidth
                            slotProps={{input: {readOnly: true}}}
                            sx={textFieldSx}
                        />
                    </Grid>
                    <Grid size={{xs: 12, md: 4}}>
                        <TextField
                            id="drom_full_vehicle_weight_kg"
                            label="Масса Drom + места × 75, кг"
                            value={metrics.dromFullMassKg === null ? "" : formatMetric(metrics.dromFullMassKg)}
                            helperText={
                                metrics.dromFullMassKg === null
                                    ? "Нужны масса Drom и кол-во мест (блок 4)"
                                    : ""
                            }
                            fullWidth
                            slotProps={{input: {readOnly: true}}}
                            sx={textFieldSx}
                        />
                    </Grid>
                    <Grid size={{xs: 12, md: 4}}>
                        <TextField
                            id="calculated_axle_mass_kg"
                            label="Расчетная масса, кг"
                            value={metrics.calculatedAxleMassKg === null ? "" : formatMetric(metrics.calculatedAxleMassKg)}
                            error={Boolean(dromMassError)}
                            helperText={
                                dromMassError ||
                                (metrics.calculatedMassRange
                                    ? `Допустимо: ${formatMassKg(metrics.calculatedMassRange.min)}–${formatMassKg(metrics.calculatedMassRange.max)} кг`
                                    : "Сравнение с массой Drom пропускается")
                            }
                            fullWidth
                            slotProps={{input: {readOnly: true}}}
                            sx={textFieldSx}
                        />
                    </Grid>
                </Grid>
            )}

            <Box sx={{mt: 3, overflowX: "auto"}}>
                <Typography variant="h6" sx={subsectionTitleSx}>
                    Проверка расчетных показателей
                </Typography>
                <Table size="small" sx={{minWidth: 620}} aria-label="Проверка расчетных показателей тормозной системы">
                    <TableHead>
                        <TableRow>
                            <TableCell>Показатель</TableCell>
                            <TableCell align="right">Расчет</TableCell>
                            <TableCell>Допустимый диапазон</TableCell>
                            <TableCell>Проверка</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {metricRows.map((metric) => {
                            const hasValue = metric.value !== null;
                            const inRange = hasValue && metric.value >= metric.min && metric.value <= metric.max;
                            const state = !hasValue
                                ? {label: "Недостаточно данных", color: "text.secondary"}
                                : inRange
                                    ? {label: "В норме", color: "success.main"}
                                    : {label: "Вне диапазона", color: "error.main"};

                            return (
                                <TableRow key={metric.label}>
                                    <TableCell>{metric.label}</TableCell>
                                    <TableCell align="right">
                                        {formatMetric(metric.value)}{metric.unit ? ` ${metric.unit}` : ""}
                                    </TableCell>
                                    <TableCell>
                                        {formatMetric(metric.min)}–{formatMetric(metric.max)}{metric.unit ? ` ${metric.unit}` : ""}
                                    </TableCell>
                                    <TableCell sx={{color: state.color, fontWeight: 700}}>
                                        {state.label}
                                    </TableCell>
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </Box>
        </Paper>
    );
}

export default ProtocolInspectionBrakes;