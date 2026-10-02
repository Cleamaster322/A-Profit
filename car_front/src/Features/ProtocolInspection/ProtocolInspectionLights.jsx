import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import { renderField, renderSelect, renderLightPair } from "./protocolInspectionHelpers.jsx";

function ProtocolInspectionLights({
  form,
  handleChange,
  textFieldSx,
  selectFieldSx,
  sectionPaperSx,
  sectionTitleSx,
}) {
  const lightPairs = [
    ["Фара дальнего света", "high_beam_count", "high_beam_color", [2, 4]],
    ["Передняя ПТФ", "front_fog_count", "front_fog_color", [2]],
    ["Фонарь заднего хода", "reverse_light_count", "reverse_light_color", [1, 2]],
    ["Указатели поворота", "turn_signal_count", "turn_signal_color", [2, 4, 6]],
    ["Передний габаритный огонь", "front_position_light_count", "front_position_light_color", [2]],
    ["Задний габаритный огонь", "rear_position_light_count", "rear_position_light_color", [2]],
    ["Сигнал торможения основной", "main_brake_signal_count", "main_brake_signal_color", [2]],
    ["Сигнал торможения дополнительный", "additional_brake_signal_count", "additional_brake_signal_color", [1, 2]],
    ["Задний ПТФ", "rear_fog_count", "rear_fog_color", [1, 2]],
    ["Подсветка госномера", "plate_light_count", "plate_light_color", [1, 2]],
    ["ДХО", "daytime_running_light_count", "daytime_running_light_color", [2]],
    ["Стояночные огни", "parking_light_count", "parking_light_color", [2]],
  ];

  return (
    <Paper sx={sectionPaperSx}>
      <Typography variant="h5" sx={sectionTitleSx}>
        7. Осветительные приборы
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

      <Divider sx={{ my: 3 }} />

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Фары ближнего света: верхняя точка, мм",
          name: "low_beam_upper_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Фары ближнего света: нижняя точка, мм",
          name: "low_beam_lower_point_mm",
          md: 6,
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "ПТФ: верхняя точка, мм",
          name: "fog_light_upper_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "ПТФ: нижняя точка, мм",
          name: "fog_light_lower_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "ПТФ: левая по ширине, мм",
          name: "fog_light_left_distance_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "ПТФ: правая по ширине, мм",
          name: "fog_light_right_distance_mm",
          md: 6,
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Основной сигнал торможения: верхняя точка, мм",
          name: "brake_signal_upper_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Основной сигнал торможения: нижняя точка, мм",
          name: "brake_signal_lower_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Основной сигнал торможения: левая по ширине, мм",
          name: "brake_signal_left_distance_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Основной сигнал торможения: правая по ширине, мм",
          name: "brake_signal_right_distance_mm",
          md: 6,
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Доп. сигнал: от нижнего края стекла, мм",
          name: "additional_brake_signal_from_glass_edge_mm",
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Доп. сигнал: от опорной поверхности, мм",
          name: "additional_brake_signal_from_support_surface_mm",
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Доп. сигнал: смещение оптического центра, мм",
          name: "additional_brake_signal_optical_center_shift_mm",
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Задние ПТФ: верхняя точка, мм",
          name: "rear_fog_upper_point_mm",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Задние ПТФ: нижняя точка, мм",
          name: "rear_fog_lower_point_mm",
          md: 6,
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
        {renderSelect({
          form,
          handleChange,
          selectFieldSx,
          label: "Омыватели фар",
          name: "headlight_washer_present",
          md: 6,
          options: [
            { value: "yes", label: "Наличие" },
            { value: "no", label: "Отсутствие" },
          ],
        })}
      </Grid>

      <Grid container spacing={2} sx={{ mb: 2 }}>
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

      <Grid container spacing={2}>
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Частота мерцания, пр./мин.",
          name: "turn_signal_frequency_per_min",
          md: 6,
        })}
        {renderField({
          form,
          handleChange,
          textFieldSx,
          label: "Частота мерцания, Гц",
          name: "turn_signal_frequency_hz",
          md: 6,
        })}
      </Grid>
    </Paper>
  );
}

export default ProtocolInspectionLights;