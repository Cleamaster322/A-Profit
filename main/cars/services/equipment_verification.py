"""
Поверки СИ и аттестации ИО для таблиц «Средства измерения» / «Испытательное оборудование»
в протоколе и техзаписи.

Поверка действует с даты начала N месяцев: 03.12.2025 + 12 мес. -> до 02.12.2026 включительно.
В документ идет поверка, действующая на дату отбора (protocol.protocol_date). Если действуют две
(новую получили раньше окончания старой), берется начавшаяся раньше — старая, пока она действует.
"""
import calendar
from datetime import date, timedelta

from django.utils import timezone

EXPIRING_DAYS = 14


class MissingVerificationError(Exception):
    """Нет действующей поверки на дату отбора: протокол выпускать нельзя (кроме admin)."""


def add_months(day, months):
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def verification_end_date(start_date, months):
    """
    03.12.2025 + 12 мес. -> 02.12.2026. Если такого числа в месяце нет
    (29.02.2024 + 12 мес. -> 28.02.2025), действует до последнего дня месяца.
    """
    target = add_months(start_date, months)
    if target.day != start_date.day:
        return target
    return target - timedelta(days=1)


def is_active_on(verification, day):
    return verification.start_date <= day <= verification.end_date


def verification_on(verifications, day):
    """Действующая на дату поверка; при пересечении — начавшаяся раньше."""
    active = [item for item in verifications if is_active_on(item, day)]
    return min(active, key=lambda item: (item.start_date, item.id or 0)) if active else None


def nearest_verification(verifications, day):
    """Ближайшая по дате поверка (для admin, когда действующей нет)."""
    def distance(item):
        if day < item.start_date:
            return (item.start_date - day).days
        return (day - item.end_date).days

    return min(verifications, key=distance) if verifications else None


def verification_status(verification, day=None):
    """«active» / «expiring» (закончится в ближайшие 2 недели) / «expired» / «missing»."""
    day = day or timezone.localdate()
    if verification is None:
        return 'missing'
    if verification.end_date < day:
        return 'expired'
    if verification.end_date <= day + timedelta(days=EXPIRING_DAYS):
        return 'expiring'
    return 'active'


def format_verification(equipment, verification):
    """Текст ячейки как в шаблоне: «Св-во № / номер / от 03.12.2025 г., / 12 мес.»."""
    if verification is None:
        return '-'

    started = f'от {verification.start_date:%d.%m.%Y} г.,'
    if equipment.kind == 'io':
        lines = ['Протокол', f'№ {verification.number}', started, f'{verification.months} мес.']
    else:
        lines = ['Св-во №', verification.number, started, f'{verification.months} мес.']
    return '\n'.join(lines)


def protocol_sample_date(protocol):
    return getattr(protocol, 'protocol_date', None) or timezone.localdate()


def build_equipment_verification_values(protocol, allow_missing=True):
    """
    Плейсхолдеры {{ eq_si035_verification }} и список оборудования без поверки на дату отбора.

    allow_missing=True (admin, предпросмотр): вместо отсутствующей ставится ближайшая поверка.
    """
    from ..models import Equipment

    day = protocol_sample_date(protocol)
    values = {}
    missing = []

    for equipment in Equipment.objects.prefetch_related('verifications'):
        verifications = list(equipment.verifications.all())
        verification = verification_on(verifications, day)
        if verification is None:
            missing.append(equipment)
            if allow_missing:
                verification = nearest_verification(verifications, day)
        values[equipment.placeholder] = format_verification(equipment, verification)

    return values, missing


def missing_verifications_message(missing, day):
    names = '; '.join(f'{equipment.code} {equipment.name}' for equipment in missing)
    return f'Нет действующей поверки на дату отбора {day:%d.%m.%Y}: {names}.'
