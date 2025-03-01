# Generated by Django 5.0.7 on 2024-07-30 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_alter_calculation_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calculation',
            name='automation_node',
            field=models.FloatField(verbose_name='Обслуживание узла автоматики'),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='service_4_year_node',
            field=models.FloatField(verbose_name='Обслуживание узла учета до 4-х лет'),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='service_node_modem',
            field=models.FloatField(verbose_name='Обслуживание узла учета с автоматической передачей данных'),
        ),
        migrations.AlterField(
            model_name='calculation',
            name='service_node_no_modem',
            field=models.FloatField(verbose_name='Обслуживание узла учета без автоматической передачи данных'),
        ),
    ]
