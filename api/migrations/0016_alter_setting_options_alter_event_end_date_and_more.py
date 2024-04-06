# Generated by Django 5.0.3 on 2024-04-06 17:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_setting_alter_event_end_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='setting',
            options={'verbose_name': 'setting', 'verbose_name_plural': 'settings'},
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 6, 19, 52, 39, 948661, tzinfo=datetime.timezone.utc), help_text='On what day and at what time the event ends', verbose_name='end time'),
        ),
        migrations.AlterModelTable(
            name='setting',
            table='setting',
        ),
    ]
