# Generated by Django 5.0.7 on 2024-07-29 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_subscriber_i_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriber',
            name='i_number',
            field=models.IntegerField(verbose_name='Номер'),
        ),
    ]
