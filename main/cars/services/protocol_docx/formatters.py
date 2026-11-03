from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def is_empty(value):
    return value is None or value == ""


def decimal_value(value):
    if is_empty(value):
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def fmt_text(value, default=""):
    if is_empty(value):
        return default
    return str(value)


def fmt_num(value, digits=1, default=""):
    number = decimal_value(value)

    if number is None:
        return default

    number = round_half_up(number, digits)

    return str(number).replace(".", ",")


def round_half_up(value, digits):
    """Округление по обычной математике: 2,5 -> 3, 1,155 -> 1,16."""
    number = decimal_value(value)

    if number is None:
        return None

    quant = Decimal("1") if digits == 0 else Decimal("1." + ("0" * digits))
    return number.quantize(quant, rounding=ROUND_HALF_UP)


def fmt_rounded(value, digits, shown_digits, default=""):
    """
    Округлить до digits знаков и записать с shown_digits знаками.

    Разность тормозных сил: прибор дает целые -> 6,25 -> «6,00».
    Удельная тормозная сила: до сотых, запись до тысячных -> 1,156 -> «1,160».
    """
    number = round_half_up(value, digits)

    if number is None:
        return default

    return fmt_num(number, shown_digits)


def fmt_int(value, default=""):
    number = decimal_value(value)

    if number is None:
        return default

    return str(int(number))


def fmt_bool(value, true_label="Да", false_label="Нет", default=""):
    if value is True:
        return true_label
    if value is False:
        return false_label
    return default


def fmt_date(value, default=""):
    if not value:
        return default

    return value.strftime("%d.%m.%Y")


def safe_div(numerator, denominator):
    numerator = decimal_value(numerator)
    denominator = decimal_value(denominator)

    if numerator is None or denominator is None or denominator == 0:
        return None

    return numerator / denominator