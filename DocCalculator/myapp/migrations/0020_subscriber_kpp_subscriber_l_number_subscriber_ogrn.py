# Generated by Django 5.0.7 on 2024-08-03 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_subscriber_fio'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriber',
            name='kpp',
            field=models.CharField(default=0, max_length=9, verbose_name='КПП'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriber',
            name='l_number',
            field=models.CharField(default=0, max_length=11, verbose_name='Лицевой счет'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriber',
            name='ogrn',
            field=models.CharField(default=0, max_length=13, verbose_name='ОГРН'),
            preserve_default=False,
        ),
    ]
