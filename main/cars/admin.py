import shutil
from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.db import connection, transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from .models import (
    Brand,
    CarData,
    Configuration,
    Generation,
    Model,
    Protocol,
    ProtocolBrake,
    ProtocolLight,
    ProtocolMeasurement,
    ProtocolPhoto,
    ProtocolPowerSupply,
    ProtocolRoadCondition,
    ProtocolTestCondition,
)

ADMIN_USERNAME = 'admin'
CLEAR_CONFIRM_WORD = 'УДАЛИТЬ'

# Только файлы протоколов; media/generations относится к данным парсера.
PROTOCOL_MEDIA_DIRS = ('protocol_photos', 'generated_protocols')


# Protocol должен идти последним: дочерние таблицы чистятся раньше.
PROTOCOL_MODELS = (
    ProtocolPhoto,
    ProtocolBrake,
    ProtocolLight,
    ProtocolMeasurement,
    ProtocolPowerSupply,
    ProtocolRoadCondition,
    ProtocolTestCondition,
    Protocol,
)


def _only_admin_user(request):
    user = request.user
    return bool(user.is_active and user.is_authenticated and user.username == ADMIN_USERNAME)


admin.site.has_permission = _only_admin_user
admin.site.site_header = 'Администрирование'


def clear_protocol_data():
    """Удаляет протоколы и связанные данные. Brand/Model/Generation/Configuration/CarData не затрагиваются."""
    with transaction.atomic():
        for model in PROTOCOL_MODELS[:-1]:
            model.objects.all().delete()
        deleted_protocols, _ = Protocol.objects.all().delete()

    # ALTER TABLE делает неявный commit, поэтому выполняется после транзакции.
    tables = [model._meta.db_table for model in PROTOCOL_MODELS]
    with connection.cursor() as cursor:
        for table in tables:
            if connection.vendor == 'mysql':
                cursor.execute(f'ALTER TABLE `{table}` AUTO_INCREMENT = 1')
            elif connection.vendor == 'sqlite':
                cursor.execute('DELETE FROM sqlite_sequence WHERE name = %s', [table])

    media_root = Path(settings.MEDIA_ROOT)
    for dir_name in PROTOCOL_MEDIA_DIRS:
        directory = media_root / dir_name
        if not directory.is_dir():
            continue
        for item in directory.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)

    return deleted_protocols


@admin.register(Protocol)
class ProtocolAdmin(admin.ModelAdmin):
    change_list_template = 'admin/cars/protocol/change_list.html'
    list_display = ('id', 'protocol_number', 'status', 'user', 'brand_name', 'created_at')
    list_filter = ('status',)
    search_fields = ('protocol_number', 'vin', 'registration_number')

    def get_urls(self):
        custom = [
            path(
                'clear-all/',
                self.admin_site.admin_view(self.clear_all_view),
                name='cars_protocol_clear_all',
            ),
        ]
        return custom + super().get_urls()

    def clear_all_view(self, request):
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse('admin:index'))

        changelist_url = reverse('admin:cars_protocol_changelist')
        error = None

        if request.method == 'POST':
            if request.POST.get('confirm', '').strip() == CLEAR_CONFIRM_WORD:
                count = clear_protocol_data()
                self.message_user(
                    request,
                    f'База протоколов очищена (удалено записей: {count}).',
                    messages.SUCCESS,
                )
                return HttpResponseRedirect(changelist_url)
            error = f'Введите слово «{CLEAR_CONFIRM_WORD}» для подтверждения.'

        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Очистить базу протоколов',
            'protocols_count': Protocol.objects.count(),
            'confirm_word': CLEAR_CONFIRM_WORD,
            'error': error,
            'changelist_url': changelist_url,
        }
        return TemplateResponse(request, 'admin/cars/protocol/clear_all.html', context)


admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Generation)
admin.site.register(Configuration)
admin.site.register(CarData)