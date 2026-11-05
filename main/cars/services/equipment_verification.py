"""
Поверки СИ и аттестации ИО для таблиц «Средства измерения» / «Испытательное оборудование»
в протоколе и техзаписи.

Поверка действует с даты начала N месяцев: 03.12.2025 + 12 мес. -> до 02.12.2026 включительно.
В документ идет поверка, действующая на дату отбора (protocol.protocol_date). Если действуют две
(новую получили раньше окончания старой), берется начавшаяся раньше — старая, пока она действует.
Поверка с отметкой «используется при пересечении» (supersedes_previous) берется с даты своего начала;
переключатель «Используется сейчас» на странице ставит эту отметку (use_verification_now).
"""
import calendar
import re
from datetime import date, timedelta

from django.utils import timezone

EXPIRING_DAYS = 14


class MissingVerificationError(Exception):
    """Нет действующей поверки на дату отбора: протокол выпускать нельзя (кроме admin)."""


def normalize_verification_number(number):
    """Для проверки уникальности: без пробелов и без учета регистра."""
    return re.sub(r"\s+", "", number or "").casefold()


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


def is_ended(verification, day=None):
    return verification.end_date < (day or timezone.localdate())


def verification_on(verifications, day):
    """
    Действующая на дату поверка. При пересечении — начавшаяся раньше,
    но последняя действующая с отметкой supersedes_previous берется вместо всех более ранних.
    """
    active = sorted(
        (item for item in verifications if is_active_on(item, day)),
        key=lambda item: (item.start_date, item.id or 0),
    )
    if not active:
        return None

    chosen = active[0]
    for item in active[1:]:
        if getattr(item, "supersedes_previous", False):
            chosen = item
    return chosen


def nearest_verification(verifications, day):
    """Ближайшая по дате поверка (для admin, когда действующей нет)."""
    def distance(item):
        if day < item.start_date:
            return (item.start_date - day).days
        return (day - item.end_date).days

    return min(verifications, key=distance) if verifications else None


class VerificationNotActiveError(Exception):
    """Сделать «используется сейчас» можно только поверку, действующую сегодня."""


def use_verification_now(verification, day=None):
    """
    Переключатель «Используется сейчас»: среди действующих на сегодня поверок оборудования
    выбранная становится используемой, остальные — нет (как радиокнопки).
    """
    day = day or timezone.localdate()
    if verification.start_date > day:
        raise VerificationNotActiveError(
            f"Поверка начнет действовать с {verification.start_date:%d.%m.%Y} — сейчас ее использовать нельзя."
        )
    if verification.end_date < day:
        raise VerificationNotActiveError("Срок поверки закончился — использовать ее нельзя.")

    active = sorted(
        (item for item in verification.equipment.verifications.all() if is_active_on(item, day)),
        key=lambda item: (item.start_date, item.id or 0),
    )
    position = next(index for index, item in enumerate(active) if item.id == verification.id)

    for index, item in enumerate(active):
        if index < position:
            continue
        # Выбранная берется вместо более ранних, более поздние перестают ее перекрывать.
        wanted = index == position and position > 0
        if item.supersedes_previous != wanted:
            item.supersedes_previous = wanted
            item.save(update_fields=["supersedes_previous", "updated_at"])


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


def chosen_verifications(protocol, allow_missing=True):
    """
    [(оборудование, поверка или None, нет ли действующей)] для протокола.

    Закрепленная при первом «Сформировать» поверка берется всегда, пока запись есть.
    Иначе — действующая на дату отбора; allow_missing=True (admin, предпросмотр):
    вместо отсутствующей ставится ближайшая поверка.
    """
    from ..models import Equipment

    day = protocol_sample_date(protocol)
    pinned = getattr(protocol, "pinned_verifications", None) or {}
    rows = []

    for equipment in Equipment.objects.prefetch_related('verifications'):
        verifications = list(equipment.verifications.all())
        by_id = {item.id: item for item in verifications}
        verification = by_id.get(pinned.get(equipment.code))
        missing = False
        if verification is None:
            verification = verification_on(verifications, day)
        if verification is None:
            missing = True
            if allow_missing:
                verification = nearest_verification(verifications, day)
        rows.append((equipment, verification, missing))

    return rows


def build_equipment_verification_values(protocol, allow_missing=True):
    """Плейсхолдеры {{ eq_si035_verification }} и список оборудования без поверки на дату отбора."""
    rows = chosen_verifications(protocol, allow_missing)
    values = {equipment.placeholder: format_verification(equipment, verification) for equipment, verification, _ in rows}
    missing = [equipment for equipment, _, is_missing in rows if is_missing]
    return values, missing


def pin_verifications(protocol, allow_missing=False):
    """Закрепить в протоколе поверки, с которыми он выпускается (первое «Сформировать»)."""
    protocol.pinned_verifications = {
        equipment.code: verification.id
        for equipment, verification, _ in chosen_verifications(protocol, allow_missing)
        if verification is not None
    }
    protocol.save(update_fields=["pinned_verifications"])


def protocols_with_pinned(verification):
    """Номера протоколов, в которых закреплена эта поверка."""
    from ..models import Protocol

    return [
        protocol_number or str(protocol_id)
        for protocol_id, protocol_number, pinned in (
            Protocol.objects.exclude(pinned_verifications={})
            .values_list("id", "protocol_number", "pinned_verifications")
        )
        if verification.id in (pinned or {}).values()
    ]


def missing_verifications_message(missing, day):
    names = '; '.join(f'{equipment.code} {equipment.name}' for equipment in missing)
    return f'Нет действующей поверки на дату отбора {day:%d.%m.%Y}: {names}.'
