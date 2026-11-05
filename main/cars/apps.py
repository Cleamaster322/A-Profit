import logging
import os
import sys
import threading
import time

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def is_server_start():
    # Только запуск сервера (runserver), не migrate / test / shell. При автоперезагрузке
    # runserver поднимает два процесса — работаем в дочернем (RUN_MAIN) или при --noreload.
    if sys.argv[1:2] != ['runserver']:
        return False
    return os.environ.get('RUN_MAIN') == 'true' or '--noreload' in sys.argv


def check_verifications_after_start():
    from django.db import connection

    from .services.verification_notifications import send_daily_verification_status

    time.sleep(5)  # дать серверу подняться
    try:
        send_daily_verification_status()
    except Exception:
        logger.exception('Проверка сроков поверок при запуске сервера не удалась')
    finally:
        connection.close()


class CarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cars'

    def ready(self):
        # Сервер включают каждое утро: при запуске пишем в Telegram о скоро заканчивающихся поверках
        # или что всё в порядке (раз в день).
        if is_server_start():
            threading.Thread(target=check_verifications_after_start, daemon=True).start()
