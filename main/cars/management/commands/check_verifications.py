from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from cars.services.verification_notifications import (
    TelegramError,
    build_message,
    build_ok_message,
    expiring_verifications,
    send_daily_verification_status,
    send_test_notification,
    telegram_configured,
)


class Command(BaseCommand):
    help = "Проверить сроки поверок и отправить в Telegram напоминание о тех, что заканчиваются в ближайшие 14 дней."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Только показать сообщение, не отправлять.")
        parser.add_argument(
            "--test",
            action="store_true",
            help="Отправить тестовое сообщение с ближайшими по сроку поверками (без отметки «уже напоминали»).",
        )

    def handle(self, *args, **options):
        today = timezone.localdate()

        if options["dry_run"]:
            verifications = expiring_verifications(today)
            self.stdout.write(build_message(verifications, today) if verifications else build_ok_message(today))
            return

        if not telegram_configured():
            raise CommandError("В .env нет TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID.")

        try:
            if options["test"]:
                count = send_test_notification(today)
                self.stdout.write(self.style.SUCCESS(f"Тестовое сообщение отправлено ({count} поверки в примере)."))
                return

            sent = send_daily_verification_status(today)
        except TelegramError as error:
            raise CommandError(f"Telegram: {error}") from error

        if sent == "expiring":
            self.stdout.write(self.style.SUCCESS("Отправлен список поверок, которые скоро закончатся."))
        elif sent == "ok":
            self.stdout.write(self.style.SUCCESS("Отправлено: поверки в порядке."))
        else:
            self.stdout.write("Сообщение не отправлено: сегодня уже писали.")
