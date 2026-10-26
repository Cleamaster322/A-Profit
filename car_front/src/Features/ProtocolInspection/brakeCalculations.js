const GRAVITY = 9.8;
// Масса Drom — для пустой ТС; для сравнения с нагрузкой на оси добавляем по 75 кг на место.
const PASSENGER_MASS_KG = 75;
// Расчетная масса (по осям) должна быть на 1–5 % меньше массы Drom с учетом мест.
const CALCULATED_MASS_MIN_SHARE = 0.95;
const CALCULATED_MASS_MAX_SHARE = 0.99;
const MASS_EPSILON = 1e-9;

function parseMeasurement(value) {
  if (value === null || value === undefined) return null;
  const normalized = String(value).trim().replace(/\s/g, "").replace(",", ".");
  if (!normalized || normalized === "-") return null;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function sumAvailable(values) {
  const available = values.filter((value) => value !== null);
  return available.length ? available.reduce((total, value) => total + value, 0) : null;
}

function getCalculatedAxleMassKg(form) {
  const axle1 = parseMeasurement(form.axle1_load_kg);
  const axle2 = parseMeasurement(form.axle2_load_kg);
  return axle1 === null || axle2 === null ? null : axle1 + axle2;
}

// «Кол-во мест» хранится по рядам: «2/3» = 5, «2/2/3» = 7, «2» = 2.
export function countSeats(value) {
  if (value === null || value === undefined) return null;
  const parts = String(value).split("/").map((part) => part.trim());
  if (!parts.length || !parts.every((part) => /^\d+$/.test(part))) return null;
  return parts.reduce((total, part) => total + Number(part), 0);
}

function getDromFullMassKg(dromMassKg, seatsCount) {
  const dromMass = parseMeasurement(dromMassKg);
  const seats = countSeats(seatsCount);
  return dromMass === null || seats === null ? null : dromMass + seats * PASSENGER_MASS_KG;
}

// Удельная тормозная сила считается только по нагрузкам на оси (они вводятся всегда).
function calcSpecificBrakeForce(form, forceFieldNames) {
  const forceSum = sumAvailable(forceFieldNames.map((fieldName) => parseMeasurement(form[fieldName])));
  const massKg = getCalculatedAxleMassKg(form);
  if (forceSum === null || massKg === null || massKg === 0) return null;

  return forceSum / (massKg * GRAVITY / 1000);
}

function calcRelativeDifference(leftValue, rightValue) {
  const left = parseMeasurement(leftValue);
  const right = parseMeasurement(rightValue);
  if (left === null || right === null) return null;

  const maximum = Math.max(left, right);
  if (maximum === 0) return null;

  return 100 * (maximum - Math.min(left, right)) / maximum;
}

// Границы для расчетной массы: от 95 % до 99 % массы Drom с учетом мест (включительно).
function getCalculatedMassRange(fullMassKg) {
  if (fullMassKg === null) return null;
  return {
    min: fullMassKg * CALCULATED_MASS_MIN_SHARE,
    max: fullMassKg * CALCULATED_MASS_MAX_SHARE,
  };
}

// 950 → «950», 1377.5 → «1377,5».
export function formatMassKg(value) {
  return String(Math.round(value * 100) / 100).replace(".", ",");
}

export function calculateBrakeMetrics(form, dromMassKg = form.vehicle_weight_kg) {
  return {
    dromMassKg: parseMeasurement(dromMassKg),
    dromFullMassKg: getDromFullMassKg(dromMassKg, form.seats_count),
    calculatedMassRange: getCalculatedMassRange(getDromFullMassKg(dromMassKg, form.seats_count)),
    calculatedAxleMassKg: getCalculatedAxleMassKg(form),
    serviceSpecificForce: calcSpecificBrakeForce(form, [
      "service_brake_front_left_kn",
      "service_brake_front_right_kn",
      "service_brake_rear_left_kn",
      "service_brake_rear_right_kn",
    ]),
    parkingSpecificForce: calcSpecificBrakeForce(form, [
      "parking_brake_left_kn",
      "parking_brake_right_kn",
    ]),
    axle1DifferencePct: calcRelativeDifference(
      form.service_brake_front_left_kn,
      form.service_brake_front_right_kn,
    ),
    axle2DifferencePct: calcRelativeDifference(
      form.service_brake_rear_left_kn,
      form.service_brake_rear_right_kn,
    ),
  };
}

// Drom дает массу пустой ТС, поэтому нагрузку на оси сравниваем с массой Drom + места * 75 кг:
// расчетная масса должна быть на 1–5 % меньше. Без массы Drom или мест проверка пропускается.
export function getDromMassComparisonError(form, dromMassKg = form.vehicle_weight_kg) {
  const range = getCalculatedMassRange(getDromFullMassKg(dromMassKg, form.seats_count));
  const calculatedMass = getCalculatedAxleMassKg(form);
  if (range === null || calculatedMass === null) return "";
  if (calculatedMass >= range.min - MASS_EPSILON && calculatedMass <= range.max + MASS_EPSILON) return "";

  return `Расчетная масса ${formatMassKg(calculatedMass)} кг вне диапазона ${formatMassKg(range.min)}–${formatMassKg(range.max)} кг (на 1–5 % меньше массы Drom с учетом мест).`;
}

export function validateBrakeMetrics(form, dromMassKg = form.vehicle_weight_kg) {
  const metrics = calculateBrakeMetrics(form, dromMassKg);
  const checks = [
    {value: metrics.serviceSpecificForce, min: 0.52, max: 0.98, fieldName: "service_brake_front_left_kn", label: "Удельная тормозная сила рабочей тормозной системы"},
    {value: metrics.parkingSpecificForce, min: 0.18, max: 0.48, fieldName: "parking_brake_left_kn", label: "Удельная тормозная сила стояночной тормозной системы"},
    {value: metrics.axle1DifferencePct, min: 0, max: 14, fieldName: "service_brake_front_left_kn", label: "Относительная разность тормозных сил колес 1-й оси"},
    {value: metrics.axle2DifferencePct, min: 0, max: 14, fieldName: "service_brake_rear_left_kn", label: "Относительная разность тормозных сил колес 2-й оси"},
  ];
  const errors = checks
    .filter(({value, min, max}) => value !== null && (value < min || value > max))
    .map(({value, min, max, fieldName, label}) => ({
      fieldName,
      message: `${label}: ${value.toFixed(2)} вне допустимого диапазона ${min.toFixed(2)}–${max.toFixed(2)}.`,
    }));
  const massError = getDromMassComparisonError(form, dromMassKg);

  if (massError) errors.unshift({fieldName: "axle1_load_kg", message: massError});
  return errors;
}