# Generated by Django 5.0.7 on 2024-07-31 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0018_alter_calculation_automation_node_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='fio',
            field=models.CharField(default=0, max_length=255, verbose_name='ФИО руководителя'),
            preserve_default=False,
        ),
    ]
