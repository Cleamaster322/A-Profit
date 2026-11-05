from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from cars.services.verification_notifications import TelegramError, recent_chats


class Command(BaseCommand):
    help = "Показать номера чатов, которые недавно писали боту (для TELEGRAM_CHAT_ID в .env)."

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("В .env нет TELEGRAM_BOT_TOKEN.")

        try:
            chats = recent_chats()
        except TelegramError as error:
            raise CommandError(f"Telegram: {error}") from error

        if not chats:
            self.stdout.write(
                "Пока никто не писал боту. Откройте бота в Telegram и нажмите «Запустить» "
                "(или добавьте его в группу и напишите там сообщение), затем запустите команду снова."
            )
            return

        self.stdout.write("Чаты, которые писали боту (номер — в TELEGRAM_CHAT_ID, несколько через запятую):")
        for chat_id, label in chats:
            self.stdout.write(f"  {chat_id}  — {label}")
