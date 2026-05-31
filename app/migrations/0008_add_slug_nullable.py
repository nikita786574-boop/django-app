from django.db import migrations, models


class Migration(migrations.Migration):
    """Шаг 1/3: добавляем slug как nullable без unique, чтобы заполнить данные."""

    dependencies = [
        ('app', '0007_parameterimportance_relation_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsystem',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='parameters',
            name='slug',
            field=models.SlugField(blank=True, max_length=320, null=True),
        ),
    ]
