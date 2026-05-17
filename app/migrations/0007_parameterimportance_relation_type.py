from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_alter_parameterimportance_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameterimportance',
            name='relation_type',
            field=models.CharField(
                blank=True,
                choices=[('A1', 'А1 — Противоречивая'), ('A2', 'А2 — Согласованная'), ('A3', 'А3 — Нейтральная')],
                help_text='Тип связи между параметрами (А1/А2/А3)',
                max_length=2,
                null=True,
            ),
        ),
    ]
