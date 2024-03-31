# Generated by Django 5.0.3 on 2024-03-27 22:06

import django.core.validators
import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('first_contact', models.DateTimeField(auto_now_add=True, help_text='The date the contact contacted for the first time', verbose_name='first contact')),
                ('full_name', models.CharField(help_text='The name of the person who contacted', max_length=100, verbose_name='full name')),
                ('event_date', models.DateTimeField(blank=True, help_text='The date of the event the contact want to do', null=True, verbose_name='event date')),
                ('phone', models.CharField(help_text='The phone number of the contact', max_length=10, verbose_name='phone')),
                ('confirm_date', models.DateTimeField(blank=True, help_text='If values represent the date the contact confirmed the event', null=True, verbose_name='confirm date')),
                ('additional_info', models.TextField(help_text='A transcribed whatsapp conversation', verbose_name='additional information')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
                'db_table': 'contact',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('image', models.ImageField(blank=True, help_text='Not required. The photo will be stored in the system', null=True, upload_to='item_images', verbose_name='profile pic')),
                ('quantity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='quantity')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
                'db_table': 'item',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('city', models.CharField(help_text='The city of the location', max_length=100, verbose_name='city')),
                ('name', models.CharField(help_text='The name of the location', max_length=100, verbose_name='name')),
                ('latitude', models.FloatField(blank=True, help_text='latidudine della location', null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)], verbose_name='latitudine')),
                ('longitude', models.FloatField(blank=True, help_text='longitudine della location', null=True, validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)], verbose_name='longitudine')),
            ],
            options={
                'verbose_name': 'location',
                'verbose_name_plural': 'locations',
                'db_table': 'location',
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('first_name', models.CharField(max_length=100, verbose_name='first name')),
                ('last_name', models.CharField(max_length=100, verbose_name='last name')),
                ('profile_pic', models.ImageField(blank=True, help_text='Not required. The photo will be stored in the system', null=True, upload_to='profile_pics', verbose_name='profile pic')),
                ('phone', models.CharField(help_text='The phone number of the provider', max_length=10, verbose_name='phone')),
                ('email', models.EmailField(max_length=100, verbose_name='email')),
                ('company_name', models.CharField(max_length=100, verbose_name='company name')),
                ('vat_number', models.CharField(max_length=100, verbose_name='vat number')),
            ],
            options={
                'verbose_name': 'provider',
                'verbose_name_plural': 'providers',
                'db_table': 'provider',
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(help_text='The name of the type', max_length=100, verbose_name='name')),
                ('description', models.CharField(blank=True, help_text='The description of the event type', max_length=100, null=True, verbose_name='description')),
            ],
            options={
                'verbose_name': 'type',
                'verbose_name_plural': 'types',
                'db_table': 'type',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.DateField(auto_now_add=True, verbose_name='date')),
                ('start_time', models.TimeField(verbose_name='start time')),
                ('end_time', models.TimeField(verbose_name='end time')),
                ('distance', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='distance')),
                ('payment', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='payment')),
                ('extra', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='extra')),
                ('busker', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='busker')),
                ('sent', models.DateField(blank=True, null=True, verbose_name='sent')),
                ('paid', models.DateField(blank=True, null=True, verbose_name='paid')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.contact', verbose_name='contact')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.location', verbose_name='location')),
                ('provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.provider', verbose_name='provider')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.type', verbose_name='type')),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'db_table': 'event',
            },
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('code', models.CharField(max_length=3, verbose_name='code')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.expensecategory', verbose_name='parent category')),
            ],
            options={
                'verbose_name': 'expense category',
                'verbose_name_plural': 'expense categories',
                'db_table': 'expense_category',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.DateField(auto_now_add=True, verbose_name='date')),
                ('amount', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='amount')),
                ('description', models.TextField(help_text='The description of the expense', verbose_name='description')),
                ('depreciable', models.BooleanField(default=0, help_text='If true the amount will be split in 5 tax years', verbose_name='depreciable')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.event', verbose_name='event')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.expensecategory', verbose_name='category')),
            ],
            options={
                'verbose_name': 'expense',
                'verbose_name_plural': 'expenses',
                'db_table': 'expense',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('date', models.DateField(auto_now_add=True, verbose_name='date')),
                ('content', models.TextField(help_text='The content of the note', verbose_name='content')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.event', verbose_name='event')),
            ],
            options={
                'verbose_name': 'note',
                'verbose_name_plural': 'notes',
                'db_table': 'note',
            },
        ),
    ]
