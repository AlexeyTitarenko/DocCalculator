# Generated by Django 4.2.14 on 2024-07-27 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_calculation_heat_exchanger_disassemble'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculation',
            name='heat_exchanger_dis',
            field=models.DecimalField(decimal_places=2, default=15276, max_digits=10, verbose_name='Промывка теплообменника с разборкой'),
            preserve_default=False,
        ),
    ]
