# Generated by Django 5.0.3 on 2024-04-05 21:12

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_event_end_date_alter_event_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 5, 23, 12, 41, 705694, tzinfo=datetime.timezone.utc), help_text='On what day and at what time the event ends', verbose_name='end time'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='On what day and at what time the event starts', verbose_name='start time'),
        ),
        migrations.AlterField(
            model_name='expensecategory',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='name'),
        ),
    ]