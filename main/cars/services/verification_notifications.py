"""
Сообщение в Telegram о скором окончании поверок оборудования.

Проверка идет при запуске сервера (cars/apps.py) и командой `manage.py check_verifications`.
В список попадает последняя поверка каждого прибора, если она заканчивается в ближайшие
14 дней или уже закончилась — то есть новую еще не внесли. Одно сообщение в день со списком;
одна и та же поверка — не чаще раза в день (EquipmentVerification.expiry_notified_on).
Если таких поверок нет — раз в день сообщение «всё в порядке» (ReminderLog).

Бот и чаты — в .env: TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID (номер чата: `manage.py telegram_chat_id`).
"""
import json
import logging
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

from .equipment_verification import EXPIRING_DAYS

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
# Ограничение Telegram — 4096 символов в сообщении; длинный список делим на части.
MESSAGE_LIMIT = 3900


class TelegramError(Exception):
    """Telegram не принял запрос; текст — для пользователя."""


def telegram_configured():
    return bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_IDS)


def call_telegram(method, payload=None):
    url = TELEGRAM_API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    data = urlencode(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=data)
    try:
        with urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except OSError as error:
        raise TelegramError(f"Нет связи с Telegram: {error}") from error

    if not result.get("ok"):
        raise TelegramError(result.get("description") or "Telegram отклонил запрос")
    return result.get("result")


def split_message(text):
    """Делит текст по строкам на части не длиннее лимита Telegram."""
    parts, current = [], ""
    for line in text.split("\n"):
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > MESSAGE_LIMIT and current:
            parts.append(current)
            current = line
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def send_telegram_message(text):
    for chat_id in settings.TELEGRAM_CHAT_IDS:
        for part in split_message(text):
            call_telegram("sendMessage", {"chat_id": chat_id, "text": part, "disable_web_page_preview": "true"})


def expiring_verifications(today=None):
    """Последние поверки приборов, у которых до окончания 14 дней или меньше."""
    today = today or timezone.localdate()
    limit = today + timedelta(days=EXPIRING_DAYS)
    return [item for item in latest_verifications() if item.end_date <= limit]


def latest_verifications():
    """Последняя по сроку поверка каждого прибора, от ближайшего окончания."""
    from ..models import Equipment

    result = []
    for equipment in Equipment.objects.prefetch_related("verifications"):
        verifications = list(equipment.verifications.all())
        if verifications:
            result.append(max(verifications, key=lambda item: (item.end_date, item.id)))
    return sorted(result, key=lambda item: (item.end_date, item.equipment.sort_order))


def days_left_text(verification, today):
    days = (verification.end_date - today).days
    if days < 0:
        return "срок уже закончился"
    if days == 0:
        return "последний день"
    return f"осталось {days} дн."


def build_message(verifications, today, title=None):
    count = len(verifications)
    title = title or f"Поверки оборудования: истекают в ближайшие {EXPIRING_DAYS} дней ({count} шт.)"
    kind = {"si": "Св-во №", "io": "Протокол №"}
    lines = [
        f"• {item.equipment.code} {item.equipment.name} — {kind.get(item.equipment.kind, '№')} {item.number}, "
        f"действует до {item.end_date:%d.%m.%Y} ({days_left_text(item, today)})"
        for item in verifications
    ]
    return "\n".join([
        title,
        "",
        "У следующего оборудования лаборатории скоро заканчивается срок поверки (аттестации):",
        "",
        *lines,
        "",
        "Без действующей поверки протоколы с этим оборудованием выпустить будет нельзя.",
        "Когда получите новые свидетельства, внесите их на сайте: «Поверки оборудования».",
    ])


def send_expiry_notifications(today=None):
    """
    Отправляет одно сообщение со списком поверок, о которых сегодня еще не писали.
    Возвращает число поверок в сообщении (0 — сообщение не нужно или Telegram не настроен).
    """
    today = today or timezone.localdate()
    pending = [item for item in expiring_verifications(today) if item.expiry_notified_on != today]
    if not pending:
        return 0

    if not telegram_configured():
        logger.warning(
            "Напоминание о поверках не отправлено: в .env нет TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID (%s шт.)",
            len(pending),
        )
        return 0

    send_telegram_message(build_message(pending, today))

    for item in pending:
        item.expiry_notified_on = today
        item.save(update_fields=["expiry_notified_on"])

    logger.info("Напоминание о поверках отправлено в Telegram: %s шт.", len(pending))
    return len(pending)


OK_REMINDER_KIND = "verifications_ok"


def build_ok_message(today):
    lines = [
        "Поверки оборудования: всё в порядке",
        "",
        f"Ни одна поверка не заканчивается в ближайшие {EXPIRING_DAYS} дней.",
    ]
    nearest = next(iter(latest_verifications()), None)
    if nearest is not None:
        lines.append(
            f"Ближайшая: {nearest.equipment.code} {nearest.equipment.name} — "
            f"действует до {nearest.end_date:%d.%m.%Y} ({days_left_text(nearest, today)})."
        )
    return "\n".join(lines)


def send_daily_verification_status(today=None):
    """
    Ежедневная проверка при запуске сервера: список скоро заканчивающихся поверок
    или, если таких нет, «всё в порядке». Каждое — не чаще раза в день.
    Возвращает «expiring», «ok» или None (сегодня уже писали / Telegram не настроен).
    """
    from ..models import ReminderLog

    today = today or timezone.localdate()
    if expiring_verifications(today):
        return "expiring" if send_expiry_notifications(today) else None

    if not telegram_configured():
        logger.warning("Сообщение «поверки в порядке» не отправлено: в .env нет TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID")
        return None
    if ReminderLog.objects.filter(kind=OK_REMINDER_KIND, day=today).exists():
        return None

    send_telegram_message(build_ok_message(today))
    ReminderLog.objects.get_or_create(kind=OK_REMINDER_KIND, day=today)
    logger.info("Сообщение «поверки в порядке» отправлено в Telegram")
    return "ok"


def send_test_notification(today=None, count=3):
    """Тестовое сообщение: ближайшие по сроку поверки, без отметки «уже напоминали»."""
    today = today or timezone.localdate()
    verifications = latest_verifications()[:count]
    send_telegram_message(build_message(
        verifications,
        today,
        title="Тестовое сообщение: так будет выглядеть напоминание о поверках",
    ))
    return len(verifications)


def recent_chats():
    """Чаты, которые недавно писали боту или добавили его в группу: [(chat_id, подпись)]."""
    chats = {}
    for update in call_telegram("getUpdates") or []:
        for key in ("message", "edited_message", "channel_post", "my_chat_member", "chat_member"):
            chat = (update.get(key) or {}).get("chat")
            if not chat:
                continue
            if chat.get("type") == "private":
                name = " ".join(filter(None, [chat.get("first_name"), chat.get("last_name")]))
                label = f"личный чат: {name or chat.get('username') or '—'}"
            else:
                label = f"группа: {chat.get('title') or '—'}"
            chats[chat["id"]] = label
    return list(chats.items())
