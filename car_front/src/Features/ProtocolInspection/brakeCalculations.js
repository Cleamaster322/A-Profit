const GRAVITY = 9.8;

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

function getVehicleMassKg(form, dromMassKg) {
  const calculatedAxleMass = getCalculatedAxleMassKg(form);
  if (calculatedAxleMass !== null && calculatedAxleMass !== 0) return calculatedAxleMass;
  return parseMeasurement(dromMassKg);
}

function calcSpecificBrakeForce(form, forceFieldNames, dromMassKg) {
  const forceSum = sumAvailable(forceFieldNames.map((fieldName) => parseMeasurement(form[fieldName])));
  const massKg = getVehicleMassKg(form, dromMassKg);
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

export function calculateBrakeMetrics(form, dromMassKg = form.vehicle_weight_kg) {
  return {
    dromMassKg: parseMeasurement(dromMassKg),
    calculatedAxleMassKg: getCalculatedAxleMassKg(form),
    serviceSpecificForce: calcSpecificBrakeForce(form, [
      "service_brake_front_left_kn",
      "service_brake_front_right_kn",
      "service_brake_rear_left_kn",
      "service_brake_rear_right_kn",
    ], dromMassKg),
    parkingSpecificForce: calcSpecificBrakeForce(form, [
      "parking_brake_left_kn",
      "parking_brake_right_kn",
    ], dromMassKg),
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

export function getDromMassComparisonError(form, dromMassKg = form.vehicle_weight_kg) {
  const dromMass = parseMeasurement(dromMassKg);
  const calculatedMass = getCalculatedAxleMassKg(form);
  if (dromMass === null || calculatedMass === null || calculatedMass <= dromMass) return "";

  return `Суммарная нагрузка на оси (${calculatedMass.toFixed(2)} кг) превышает массу Drom (${dromMass.toFixed(2)} кг). Уменьшите нагрузку на оси.`;
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