# Generated by Django 5.0.3 on 2024-04-06 17:48

import datetime
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_event_end_date_alter_event_start_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=500)),
                ('value_type', models.CharField(choices=[('s', 'string'), ('i', 'integer'), ('b', 'boolean'), ('f', 'float')], max_length=1)),
                ('description', models.TextField(blank=True, help_text='The description of the setting', max_length=100, null=True, verbose_name='description')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 6, 19, 48, 54, 462198, tzinfo=datetime.timezone.utc), help_text='On what day and at what time the event ends', verbose_name='end time'),
        ),
    ]
