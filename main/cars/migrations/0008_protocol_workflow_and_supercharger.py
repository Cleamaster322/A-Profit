from django.db import migrations, models


def migrate_protocol_statuses(apps, schema_editor):
    Protocol = apps.get_model('cars', 'Protocol')

    Protocol.objects.filter(status__in=['draft', 'in_progress']).update(
        status='operator'
    )
    Protocol.objects.filter(status='completed').update(status='review')


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0007_protocol_cancelled_at_protocol_cancelled_by_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "ALTER TABLE protocols MODIFY COLUMN status "
                "ENUM('draft','in_progress','completed','measurement',"
                "'operator','review','revision','approved','cancelled') "
                "NOT NULL DEFAULT 'measurement'"
            ),
            reverse_sql=(
                "ALTER TABLE protocols MODIFY COLUMN status "
                "ENUM('draft','in_progress','completed','approved','cancelled') "
                "NOT NULL DEFAULT 'draft'"
            ),
        ),
        migrations.AlterField(
            model_name='protocol',
            name='status',
            field=models.CharField(
                choices=[
                    ('measurement', 'Работа замерщика'),
                    ('operator', 'Работа оператора'),
                    ('review', 'На проверке'),
                    ('revision', 'На доработке'),
                    ('approved', 'Утверждён'),
                    ('cancelled', 'Отменён'),
                ],
                default='measurement',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='protocol',
            name='supercharger',
            field=models.CharField(
                blank=True,
                choices=[
                    ('absent', 'Отсутствует'),
                    ('compressor', 'Компрессор'),
                    ('turbo', 'Турбина'),
                    ('twin_turbo', 'Твин-турбо'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(
            migrate_protocol_statuses,
            migrations.RunPython.noop,
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE protocols MODIFY COLUMN status "
                "ENUM('measurement','operator','review','revision',"
                "'approved','cancelled') NOT NULL DEFAULT 'measurement'"
            ),
            reverse_sql=(
                "ALTER TABLE protocols MODIFY COLUMN status "
                "ENUM('draft','in_progress','completed','approved','cancelled') "
                "NOT NULL DEFAULT 'draft'"
            ),
        ),
    ]