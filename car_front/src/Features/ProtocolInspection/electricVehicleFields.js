// Поля, которые не относятся к электромобилю: при «Вид топлива» = «Электро» они скрыты
// (у замерщика и у оператора) и очищаются при сохранении протокола.
export const ELECTRIC_HIDDEN_FIELDS = [
    "mufflers_count",
    "engine_layout",
    "cylinder_layout",
    "cylinders_count",
    "supercharger",
    "exhaust_noise_constant_db",
    "exhaust_noise_deceleration_db",
    "co_min_pct",
    "co_max_pct",
    "light_absorption_1",
    "light_absorption_2",
    "light_absorption_3",
    "light_absorption_4",
    "light_absorption_5",
    "light_absorption_6",
];

export function isElectricVehicle(form) {
    return form?.fuel_type === "electric";
}

export function withoutElectricHiddenFields(form) {
    if (!isElectricVehicle(form)) {
        return form;
    }

    return {
        ...form,
        ...Object.fromEntries(ELECTRIC_HIDDEN_FIELDS.map((fieldName) => [fieldName, ""])),
    };
}
