from django.db import migrations, models


class Migration(migrations.Migration):
    """Шаг 3/3: делаем slug обязательным и уникальным."""

    dependencies = [
        ('app', '0009_backfill_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subsystem',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=255,
                unique=True,
                help_text='Идентификатор для URL (генерируется автоматически)',
            ),
        ),
        migrations.AlterField(
            model_name='parameters',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=320,
                unique=True,
                help_text='Зависимый идентификатор для URL (slug подсистемы + номер + название)',
            ),
        ),
    ]
