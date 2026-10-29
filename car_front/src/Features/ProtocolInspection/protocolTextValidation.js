const VIN_FIELD_MAX_LENGTH = 17;
// Маркировку шин вводят руками как есть (165/70 R17, 165R13LT-6PR, 6.00-12-4PR …),
// ограничение — только длина поля в БД.
const TIRE_MARKING_MAX_LENGTH = 100;
const TIRE_MARKING_FIELDS = new Set(["tire_marking_front", "tire_marking_rear"]);

export function normalizeProtocolTextField(fieldName, value) {
  if (fieldName === "vin") {
    return typeof value === "string" ? value.toUpperCase() : value;
  }

  return value;
}

export function getProtocolTextFieldError(fieldName, value) {
  if (typeof value !== "string") return "";

  if (fieldName === "vin" && value.length > VIN_FIELD_MAX_LENGTH) {
    return `VIN / № кузова / № шасси: не более ${VIN_FIELD_MAX_LENGTH} символов (сейчас ${value.length}).`;
  }

  if (TIRE_MARKING_FIELDS.has(fieldName) && value.length > TIRE_MARKING_MAX_LENGTH) {
    return `Маркировка шин: не более ${TIRE_MARKING_MAX_LENGTH} символов (сейчас ${value.length}).`;
  }

  return "";
}

export function validateProtocolTextFields(form) {
  return ["vin", ...TIRE_MARKING_FIELDS].flatMap((fieldName) => {
    const message = getProtocolTextFieldError(fieldName, form[fieldName]);
    return message ? [{fieldName, message}] : [];
  });
}
