from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


STATUS_CODES = {
    400: "bad_request",
    401: "authentication_required",
    403: "permission_denied",
    404: "not_found",
    409: "conflict",
    423: "locked",
    429: "throttled",
    500: "server_error",
    503: "service_unavailable",
}


def api_error_response(message, status_code=status.HTTP_400_BAD_REQUEST, code=None, errors=None):
    payload = {
        "detail": message,
        "code": code or STATUS_CODES.get(status_code, "api_error"),
    }

    if errors:
        payload["errors"] = errors

    return Response(payload, status=status_code)


def _message_from_data(data):
    if isinstance(data, dict):
        detail = data.get("detail") or data.get("error") or data.get("message")
        if detail:
            return str(detail)
        return "Проверьте данные запроса."

    if isinstance(data, list):
        return " ".join(str(item) for item in data)

    return str(data)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return None

    original_data = response.data
    errors = original_data if isinstance(original_data, (dict, list)) else None
    code = getattr(exc, "default_code", None) or STATUS_CODES.get(
        response.status_code,
        "api_error",
    )

    response.data = {
        "detail": _message_from_data(original_data),
        "code": code,
    }

    if errors and not (
        isinstance(errors, dict) and set(errors.keys()) <= {"detail", "code"}
    ):
        response.data["errors"] = errors

    return response
