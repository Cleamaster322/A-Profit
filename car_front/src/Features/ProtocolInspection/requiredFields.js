// Проверка «все видимые поля протокола заполнены» перед передачей дальше и «Сформировать».
// Обязательными считаются поля, которые сейчас реально показаны на странице: скрытые
// по виду топлива, режиму замерщика или условиям (нет ПТФ и т. п.) в проверку не попадают.
// Пустое поле — не заполнено; «-» — заполнено («этого нет»); в списке пустой вариант — не выбрано.
// Включается/выключается в админке: «Настройки формы протокола».

const FIELD_SELECTOR = "input[name], textarea[name], select[name]";
const SKIPPED_INPUT_TYPES = new Set(["hidden", "checkbox", "radio", "file", "button", "submit"]);

export const MISSING_FIELD_CLASS = "protocol-field-missing";

function isVisible(element) {
    return element.getClientRects().length > 0;
}

function fieldWrapper(element) {
    return element.closest(".MuiFormControl-root") || element;
}

export function findMissingRequiredFields(root) {
    if (!root) {
        return [];
    }

    const seenNames = new Set();

    return [...root.querySelectorAll(FIELD_SELECTOR)].filter((element) => {
        if (SKIPPED_INPUT_TYPES.has(element.type)) return false;
        if (element.readOnly || element.disabled) return false;
        if (element.getAttribute("aria-hidden") === "true") return false;
        if (!isVisible(element)) return false;
        if (seenNames.has(element.name)) return false;

        seenNames.add(element.name);
        return String(element.value ?? "").trim() === "";
    });
}

export function getFieldLabel(element) {
    const controlLabel = fieldWrapper(element).querySelector("label")?.textContent;
    if (controlLabel?.trim()) {
        return controlLabel.replace(/\s*\*\s*$/, "").trim();
    }

    // Поля без своей подписи (например, в строках «Ось 1 / Ось 2») — подпись над полем.
    const gridLabel = element.closest(".MuiGrid-root")?.querySelector("p, h6")?.textContent;
    return gridLabel?.trim() || element.name;
}

export function markMissingFields(root, fields) {
    if (!root) {
        return;
    }

    root.querySelectorAll(`.${MISSING_FIELD_CLASS}`).forEach((element) => {
        element.classList.remove(MISSING_FIELD_CLASS);
    });

    fields.forEach((field) => fieldWrapper(field).classList.add(MISSING_FIELD_CLASS));
}

export function clearMissingMark(element) {
    if (element?.closest) {
        fieldWrapper(element).classList.remove(MISSING_FIELD_CLASS);
    }
}

export const missingFieldSx = {
    [`& .${MISSING_FIELD_CLASS} .MuiOutlinedInput-notchedOutline`]: {
        borderColor: "#d32f2f",
        borderWidth: 2,
    },
    [`& .${MISSING_FIELD_CLASS} label`]: {
        color: "#d32f2f",
    },
};

export function buildMissingFieldsMessage(fields) {
    const labels = [...new Set(fields.map(getFieldLabel))];
    const shown = labels.slice(0, 10);
    const rest = labels.length - shown.length;

    return [
        `Не заполнено полей: ${fields.length}. Заполните их или поставьте «-», если параметра нет:`,
        ...shown.map((label) => `• ${label}`),
        ...(rest > 0 ? [`… и ещё ${rest}`] : []),
    ].join("\n");
}
