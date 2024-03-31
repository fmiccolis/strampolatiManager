from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField


# Create your models here.
class User(TimeStampedModel, AbstractUser):
    profile_pic = models.ImageField(
        verbose_name=_('profile pic'),
        upload_to='profile_pics',
        null=True,
        blank=True,
        help_text=_('Not required. The photo will be stored in the system')
    )

    class Meta:
        db_table = 'user'
        verbose_name = 'user'
        verbose_name_plural = _('users')

    def nominativo(self):
        return f"{self.first_name} {self.last_name}"

    nominativo.short_description = _('full name')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Location(TimeStampedModel):
    city = models.CharField(
        verbose_name=_('city'),
        help_text=_('The city of the location'),
        max_length=100
    )
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('The name of the location'),
        max_length=100
    )
    latitude = models.FloatField(
        verbose_name=_('latitudine'),
        help_text=_('latidudine della location'),
        validators=[MinValueValidator(-90.0000000), MaxValueValidator(90.0000000)],
        null=True,
        blank=True
    )
    longitude = models.FloatField(
        verbose_name=_('longitudine'),
        help_text=_('longitudine della location'),
        validators=[MinValueValidator(-180.0000000), MaxValueValidator(180.0000000)],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'location'
        verbose_name = 'location'
        verbose_name_plural = _('locations')

    def __str__(self):
        return f"{self.city} - {self.name}"


class Type(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('The name of the type'),
        max_length=100
    )
    description = models.TextField(
        verbose_name=_('description'),
        help_text=_('The description of the event type'),
        max_length=100,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'type'
        verbose_name = 'type'
        verbose_name_plural = _('types')

    def __str__(self):
        return f"{self.name}"


class Contact(TimeStampedModel):
    first_contact = models.DateField(
        verbose_name=_('first contact'),
        default=datetime.now,
        help_text=_("The date the contact contacted for the first time")
    )
    full_name = models.CharField(
        verbose_name=_('full name'),
        max_length=100,
        help_text=_("The name of the person who contacted")
    )
    event_date = models.DateField(
        verbose_name=_('event date'),
        help_text=_("The date of the event the contact want to do"),
        null=True,
        blank=True
    )
    phone = models.CharField(
        verbose_name=_('phone'),
        max_length=10,
        help_text=_('The phone number of the contact'),
        null=True,
        blank=True
    )
    confirm_date = models.DateField(
        verbose_name=_('confirm date'),
        null=True,
        blank=True,
        help_text=_('If values represent the date the contact confirmed the event')
    )
    additional_info = models.TextField(
        verbose_name=_('additional information'),
        help_text=_('A transcribed whatsapp conversation')
    )

    class Meta:
        db_table = 'contact'
        verbose_name = 'contact'
        verbose_name_plural = _('contacts')

    def __str__(self):
        return f"{self.full_name}"


class Provider(TimeStampedModel):
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=100
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=100
    )
    profile_pic = models.ImageField(
        verbose_name=_('profile pic'),
        upload_to='profile_pics',
        null=True,
        blank=True,
        help_text=_('Not required. The photo will be stored in the system')
    )
    phone = models.CharField(
        verbose_name=_('phone'),
        max_length=10,
        help_text=_('The phone number of the provider')
    )
    email = models.EmailField(
        verbose_name=_('email'),
        null=True,
        blank=True,
        max_length=100
    )
    company_name = models.CharField(
        verbose_name=_('company name'),
        null=True,
        blank=True,
        max_length=100
    )
    vat_number = models.CharField(
        verbose_name=_('vat number'),
        null=True,
        blank=True,
        max_length=100
    )

    class Meta:
        db_table = 'provider'
        verbose_name = 'provider'
        verbose_name_plural = _('providers')

    def nominativo(self):
        return f"{self.first_name} {self.last_name}"

    nominativo.short_description = _('full name')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Item(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    image = models.ImageField(
        verbose_name=_('image'),
        upload_to='item_images',
        null=True,
        blank=True,
        help_text=_('Not required. The photo will be stored in the system')
    )
    quantity = models.IntegerField(
        verbose_name=_('quantity'),
        default=0,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        db_table = 'item'
        verbose_name = 'item'
        verbose_name_plural = _('items')

    def __str__(self):
        return f"{self.name}"


class ExpenseCategory(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    code = models.CharField(
        verbose_name=_('code'),
        max_length=3
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('parent category')
    )

    class Meta:
        db_table = 'expense_category'
        verbose_name = 'expense category'
        verbose_name_plural = _('expense categories')

    def __str__(self):
        return f"{self.name}"


class Event(TimeStampedModel):
    date = models.DateField(
        verbose_name=_('date'),
        default=datetime.now,
        help_text=_('The date of the event')
    )
    start_time = models.TimeField(
        verbose_name=_('start time'),
        help_text=_('Create the start time initially but return to edit after the event to track the real job')
    )
    end_time = models.TimeField(
        verbose_name=_('end time'),
        help_text=_('Create the end time initially but return to edit after the event to track the real job')
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        verbose_name=_('location')
    )
    distance = models.IntegerField(
        verbose_name=_('distance'),
        default=0,
        validators=[MinValueValidator(0)]
    )
    type = models.ForeignKey(
        Type,
        on_delete=models.SET_NULL,
        verbose_name=_('type'),
        null=True,
        blank=True
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        verbose_name=_('contact'),
        null=True,
        blank=True
    )
    provider = models.ForeignKey(
        Provider,
        on_delete=models.SET_NULL,
        verbose_name=_('provider'),
        null=True,
        blank=True
    )
    agents = models.ManyToManyField(
        User,
        verbose_name=_('agents'),
        help_text=_('The agents that do the job in the event')
    )
    payment = MoneyField(
        max_digits=14, decimal_places=2, null=True, blank=True, default_currency="EUR", default=0
    )
    extra = MoneyField(
        max_digits=14, decimal_places=2, null=True, blank=True, default_currency="EUR", default=0
    )
    busker = MoneyField(
        max_digits=14, decimal_places=2, null=True, blank=True, default_currency="EUR", default=0
    )
    sent = models.DateField(
        verbose_name=_('sent'),
        null=True,
        blank=True
    )
    paid = models.DateField(
        verbose_name=_('paid'),
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'event'
        verbose_name = 'event'
        verbose_name_plural = _('events')

    def __str__(self):
        return f"{self.date} | {self.location} | {self.type}"


class Expense(TimeStampedModel):
    date = models.DateField(
        verbose_name=_('date'),
        auto_now_add=True
    )
    amount = MoneyField(
        max_digits=14, decimal_places=2, null=True, blank=True, default_currency="EUR", default=0
    )
    description = models.TextField(
        verbose_name=_('description'),
        help_text=_('The description of the expense')
    )
    depreciable = models.BooleanField(
        verbose_name=_('depreciable'),
        default=0,
        help_text=_('If true the amount will be split in 5 tax years')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('event'),
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE,
        verbose_name=_('category')
    )

    class Meta:
        db_table = 'expense'
        verbose_name = 'expense'
        verbose_name_plural = _('expenses')

    def __str__(self):
        return f"{self.date} - {self.amount}"


class Note(TimeStampedModel):
    date = models.DateField(
        verbose_name=_('date'),
        auto_now_add=True
    )
    content = models.TextField(
        verbose_name=_('content'),
        help_text=_('The content of the note')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('event'),
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'note'
        verbose_name = 'note'
        verbose_name_plural = _('notes')

    def __str__(self):
        return f"{self.date}"


class Participation:
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('user')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        verbose_name=_('event')
    )

    class Meta:
        db_table = 'participation'
        verbose_name = 'participation'
        verbose_name_plural = _('participations')

    def __str__(self):
        return f"{self.user} - {self.event}"

