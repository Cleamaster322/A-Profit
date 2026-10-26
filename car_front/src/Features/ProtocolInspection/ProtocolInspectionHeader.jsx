import { useState } from "react";

import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import FormControlLabel from "@mui/material/FormControlLabel";

import {
  headerOwnerFieldSx,
  headerOwnerRowSx,
  headerStackSx,
  headerTripleRowSx,
} from "./protocolInspectionStyles.jsx";

const HEADER_DOCUMENT_OPTIONS = [
  {value: "application", label: "Заявка"},
  {value: "passport_scan", label: "Скан паспорта гражданина РФ"},
  {value: "tpo", label: "ТПО"},
  {value: "bill_of_lading", label: "Коносамент"},
  {value: "kuts", label: "КУТС"},
  {value: "vehicle_manual", label: "Руководство по эксплуатации ТС"},
  // Текст «Иного» вводится в поле под галочками и идет в тот же список документов.
  {value: "other", label: "Иное"},
];

function stripProtocolNumber(value) {
  if (value === null || value === undefined) {
    return "";
  }

  const digits = String(value).replace(/\D/g, "");

  if (!digits) {
    return "";
  }

  return String(Number(digits));
}

function formatProtocolNumber(value) {
  if (value === null || value === undefined) {
    return "";
  }

  const digits = String(value).replace(/\D/g, "");

  if (!digits) {
    return "";
  }

  return digits.padStart(5, "0");
}

function ProtocolInspectionHeader({
  form,
  handleChange,
  textFieldSx,
  sectionPaperSx,
  sectionTitleSx,
}) {
  const [protocolNumberFocused, setProtocolNumberFocused] = useState(false);

  const protocolNumberValue = protocolNumberFocused
    ? stripProtocolNumber(form.protocol_number)
    : formatProtocolNumber(form.protocol_number);

  const handleProtocolNumberChange = (event) => {
    const digits = event.target.value.replace(/\D/g, "").slice(0, 5);

    handleChange({
      target: {
        name: "protocol_number",
        value: digits,
      },
    });
  };

  const handleProtocolNumberBlur = () => {
    setProtocolNumberFocused(false);

    const formattedValue = formatProtocolNumber(form.protocol_number);

    handleChange({
      target: {
        name: "protocol_number",
        value: formattedValue,
      },
    });
  };

  const handleHeaderDocumentChange = (value, checked) => {
    const selected = form.header_document_selections || [];
    const nextSelected = checked
      ? [...new Set([...selected, value])]
      : selected.filter((item) => item !== value);

    handleChange({
      target: {
        name: "header_document_selections",
        value: nextSelected,
      },
    });
  };

  return (
    <Paper sx={sectionPaperSx}>
      <Typography variant="h5" sx={sectionTitleSx}>
        1. Шапка документа
      </Typography>

      <Box sx={headerStackSx}>
        <Box sx={headerTripleRowSx}>
          <TextField
            fullWidth
            label="Номер протокола"
            name="protocol_number"
            value={protocolNumberValue}
            onFocus={() => setProtocolNumberFocused(true)}
            onBlur={handleProtocolNumberBlur}
            onChange={handleProtocolNumberChange}
            sx={textFieldSx}
            inputProps={{
              inputMode: "numeric",
              pattern: "[0-9]*",
              maxLength: 5,
            }}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />

          <TextField
            fullWidth
            label="Приложение к технической записи №"
            name="appendix_number"
            value={form.appendix_number || ""}
            onChange={handleChange}
            sx={textFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />

          <TextField
            fullWidth
            type="date"
            label="Дата протокола"
            name="protocol_date"
            value={form.protocol_date || ""}
            onChange={handleChange}
            sx={textFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />
        </Box>

        <Box sx={headerOwnerRowSx}>
          <TextField
            fullWidth
            label="ФИО заказчика"
            name="owner_full_name"
            value={form.owner_full_name || ""}
            onChange={handleChange}
            sx={headerOwnerFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />
          <TextField
            fullWidth
            label="Адрес заказчика"
            name="owner_address"
            value={form.owner_address || ""}
            onChange={handleChange}
            sx={headerOwnerFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />
        </Box>

        <Box sx={headerOwnerRowSx}>
          <TextField
            fullWidth
            multiline
            minRows={2}
            label="Юр. лицо"
            name="owner_legal_entity"
            value={form.owner_legal_entity || ""}
            onChange={handleChange}
            sx={textFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />
          <TextField
            fullWidth
            multiline
            minRows={2}
            label="Реквизиты"
            name="owner_requisites"
            value={form.owner_requisites || ""}
            onChange={handleChange}
            sx={textFieldSx}
            slotProps={{
              inputLabel: {
                shrink: true,
              },
            }}
          />
        </Box>

        <TextField
          fullWidth
          multiline
          minRows={2}
          label="Наименование и адрес изготовителя"
          name="manufacturer_info"
          value={form.manufacturer_info || ""}
          onChange={handleChange}
          sx={textFieldSx}
          slotProps={{
            inputLabel: {
              shrink: true,
            },
          }}
        />

        <Box>
          <Typography variant="h6" sx={{mb: 1}}>
            Документы и сведения по отбору образца
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {xs: "1fr", sm: "repeat(2, minmax(0, 1fr))"},
              columnGap: 2,
            }}
          >
            {HEADER_DOCUMENT_OPTIONS.map(({value, label}) => (
              <FormControlLabel
                key={value}
                control={(
                  <Checkbox
                    checked={(form.header_document_selections || []).includes(value)}
                    onChange={(event) => handleHeaderDocumentChange(value, event.target.checked)}
                  />
                )}
                label={label}
              />
            ))}
          </Box>

          {(form.header_document_selections || []).includes("other") && (
            <TextField
              fullWidth
              multiline
              minRows={2}
              label="Иное"
              name="header_documents_other"
              value={form.header_documents_other || ""}
              onChange={handleChange}
              sx={{...textFieldSx, mt: 1}}
              slotProps={{
                inputLabel: {
                  shrink: true,
                },
              }}
            />
          )}
        </Box>
      </Box>
    </Paper>
  );
}

export default ProtocolInspectionHeader;