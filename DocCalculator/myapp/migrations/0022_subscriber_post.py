# Generated by Django 5.0.7 on 2024-08-20 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_rename_service_4_year_node_calculation_service_four_year_node_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='post',
            field=models.CharField(default=0, max_length=255, verbose_name='Должность руководителя'),
            preserve_default=False,
        ),
    ]
