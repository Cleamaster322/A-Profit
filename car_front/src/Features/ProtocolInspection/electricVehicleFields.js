// Поля, которые не относятся к ТС с данным видом топлива: они скрыты
// (у замерщика и у оператора) и очищаются при сохранении протокола.
// Гибрид-бензин ведет себя как бензин, гибрид-дизель — как дизель.

const CO_FIELDS = ["co_min_pct", "co_max_pct"];

const LIGHT_ABSORPTION_FIELDS = [
    "light_absorption_1",
    "light_absorption_2",
    "light_absorption_3",
    "light_absorption_4",
    "light_absorption_5",
    "light_absorption_6",
];

export const ELECTRIC_HIDDEN_FIELDS = [
    "mufflers_count",
    "engine_layout",
    "cylinder_layout",
    "cylinders_count",
    "supercharger",
    "exhaust_noise_constant_db",
    "exhaust_noise_deceleration_db",
    ...CO_FIELDS,
    ...LIGHT_ABSORPTION_FIELDS,
];

export function isElectricVehicle(form) {
    return form?.fuel_type === "electric";
}

export function isPetrolLikeVehicle(form) {
    return ["petrol", "hybrid_petrol"].includes(form?.fuel_type);
}

export function isDieselLikeVehicle(form) {
    return ["diesel", "hybrid_diesel"].includes(form?.fuel_type);
}

// CO меряют только у бензиновых, коэффициент поглощения света — только у дизельных.
export function getFuelHiddenFields(form) {
    if (isElectricVehicle(form)) return ELECTRIC_HIDDEN_FIELDS;
    if (isDieselLikeVehicle(form)) return CO_FIELDS;
    if (isPetrolLikeVehicle(form)) return LIGHT_ABSORPTION_FIELDS;
    return [];
}

export function withoutFuelHiddenFields(form) {
    const hiddenFields = getFuelHiddenFields(form);

    if (!hiddenFields.length) {
        return form;
    }

    return {
        ...form,
        ...Object.fromEntries(hiddenFields.map((fieldName) => [fieldName, ""])),
    };
}
