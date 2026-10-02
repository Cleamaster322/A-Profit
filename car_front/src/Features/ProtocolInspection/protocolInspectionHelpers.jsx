import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import {getNumericRangeError} from "./numericRangeValidation.js";

export function renderField({
  form,
  handleChange,
  textFieldSx,
  label,
  name,
  md = 4,
  placeholder = "",
  multiline = false,
  minRows = 1,
}) {
  const rangeError = getNumericRangeError(name, form);

  return (
    <Grid size={{ xs: 12, md }}>
      <TextField
        id={name}
        label={label}
        name={name}
        value={form[name] ?? ""}
        onChange={handleChange}
        fullWidth
        placeholder={placeholder}
        multiline={multiline}
        minRows={minRows}
        error={Boolean(rangeError)}
        helperText={rangeError || undefined}
        sx={textFieldSx}
      />
    </Grid>
  );
}

export function renderSelect({
  form,
  handleChange,
  selectFieldSx,
  label,
  name,
  md = 4,
  options = [],
}) {
  return (
    <Grid size={{ xs: 12, md }}>
      <FormControl fullWidth size="small" variant="outlined" sx={selectFieldSx}>
        <InputLabel>{label}</InputLabel>
        <Select
          native
          name={name}
          value={form[name] ?? ""}
          onChange={handleChange}
          label={label}
          variant="outlined"
        >
          <option value=""></option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </Select>
      </FormControl>
    </Grid>
  );
}

export function renderTripleRow({
  form,
  handleChange,
  textFieldSx,
  smallLabelSx,
  items,
  marginBottom = 2,
}) {
  return (
    <Grid container spacing={2} sx={{ mb: marginBottom }}>
      {items.map((item) => (
        <Grid size={{ xs: 12, md: 4 }} key={item.name}>
          <Typography sx={smallLabelSx}>{item.label}</Typography>
          <TextField
            name={item.name}
            value={form[item.name] ?? ""}
            onChange={handleChange}
            fullWidth
            placeholder={item.placeholder ?? ""}
            sx={textFieldSx}
          />
        </Grid>
      ))}
    </Grid>
  );
}

export function renderLightPair({
  form,
  handleChange,
  textFieldSx,
  title,
  countName,
  colorName,
  countOptions,
  showColor = false,
}) {
  const countValue = form[countName] ?? "";
  const isPresent = Number(countValue) > 0;
  const countRangeError = getNumericRangeError(countName, form);

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: "minmax(220px, 1.3fr) 120px minmax(180px, 1fr)",
        alignItems: "center",
        gap: 1.5,
        width: "100%",
        maxWidth: 1280,
        py: 1,
        borderBottom: "1px solid",
        borderColor: "divider",
        "@media (max-width: 700px)": {
          gridTemplateColumns: "minmax(0, 1fr) auto",
          "& .light-title, & .light-color": {gridColumn: "1 / -1"},
          "& .light-quantity": {gridColumn: "2"},
        },
      }}
    >
      <Typography className="light-title" sx={{fontWeight: 600}}>
        {title}
      </Typography>

      <FormControlLabel
        control={(
          <Checkbox
            checked={isPresent}
            onChange={(event) => {
              const nextValue = event.target.checked ? String(countOptions[0]) : "";
              handleChange({target: {name: countName, value: nextValue}});
              if (!event.target.checked && showColor && colorName) {
                handleChange({target: {name: colorName, value: ""}});
              }
            }}
          />
        )}
        label="Есть"
        sx={{m: 0}}
      />

      {showColor ? (
        <Box className="light-color">
          <TextField
            label="Цвет"
            name={colorName}
            value={form[colorName] ?? ""}
            onChange={handleChange}
            disabled={!isPresent}
            fullWidth
            sx={textFieldSx}
          />
        </Box>
      ) : (
        <Box className="light-quantity">
          {!isPresent ? (
            <Typography color="text.secondary">Отсутствует</Typography>
          ) : countOptions.length === 1 ? (
            <Typography>{countOptions[0]} шт.</Typography>
          ) : (
            <TextField
              id={countName}
              label="Количество"
              name={countName}
              value={String(countValue)}
              onChange={handleChange}
              select
              fullWidth
              error={Boolean(countRangeError)}
              helperText={countRangeError || undefined}
              sx={textFieldSx}
            >
              {countOptions.map((count) => (
                <MenuItem key={count} value={String(count)}>{count}</MenuItem>
              ))}
            </TextField>
          )}
        </Box>
      )}
    </Box>
  );
}