const VIN_FIELD_MAX_LENGTH = 17;
const TIRE_MARKING_MAX_LENGTH = 10;
const TIRE_MARKING_FIELDS = new Set(["tire_marking_front", "tire_marking_rear"]);

export function normalizeProtocolTextField(fieldName, value) {
  if (fieldName === "vin") {
    return typeof value === "string" ? value.toUpperCase() : value;
  }

  if (!TIRE_MARKING_FIELDS.has(fieldName) || value === null || value === undefined) {
    return value;
  }

  const original = String(value).trim();
  if (!original || original === "-") return original;

  const digits = original.replace(/\D/g, "");
  if (!digits) return "";

  const width = digits.slice(0, 3);
  if (digits.length < 3) return width;

  const profile = digits.slice(3, 5);
  const base = `${width}/${profile}`;
  if (digits.length < 5) return base;

  return `${base} R${digits.slice(5)}`;
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