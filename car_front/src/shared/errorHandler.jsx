const STATUS_MESSAGES = {
    401: "Сессия истекла. Войдите в систему снова.",
    403: "Недостаточно прав для выполнения этого действия.",
    404: "Запрашиваемый объект не найден.",
    409: "Операция конфликтует с текущим состоянием данных.",
    423: "Протокол занят другим пользователем.",
    429: "Слишком много запросов. Повторите попытку позже.",
    500: "Внутренняя ошибка сервера.",
    502: "Сервер временно недоступен.",
    503: "Сервис временно недоступен. Повторите попытку позже.",
};

function stringifyErrorValue(value) {
    if (Array.isArray(value)) {
        return value.map(stringifyErrorValue).filter(Boolean).join(" ");
    }

    if (value && typeof value === "object") {
        return Object.values(value).map(stringifyErrorValue).filter(Boolean).join(" ");
    }

    return value === null || value === undefined ? "" : String(value).trim();
}

export function getApiErrorStatus(error) {
    return error?.response?.status || null;
}

export function getApiErrorMessage(error, fallback = "Не удалось выполнить запрос") {
    const status = getApiErrorStatus(error);
    const data = error?.response?.data;

    if (data && typeof data !== "string" && !(data instanceof Blob)) {
        const serverMessage = stringifyErrorValue(data.detail || data.error || data.message);

        if (serverMessage) {
            return serverMessage;
        }

        const fieldErrors = stringifyErrorValue(data.errors || data);
        if (fieldErrors) {
            return fieldErrors;
        }
    }

    if (status && STATUS_MESSAGES[status]) {
        return STATUS_MESSAGES[status];
    }

    if (!error?.response) {
        return "Сервер недоступен или отсутствует соединение с сетью.";
    }

    return fallback;
}
