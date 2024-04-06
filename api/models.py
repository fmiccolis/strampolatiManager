import decimal
import math
from datetime import datetime, timedelta
import logging
import pytz

from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField

logger = logging.getLogger("custom")

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
        verbose_name=_('latitude'),
        help_text=_('latidude of the location'),
        validators=[MinValueValidator(-90.0000000), MaxValueValidator(90.0000000)],
        null=True,
        blank=True
    )
    longitude = models.FloatField(
        verbose_name=_('longitude'),
        help_text=_('longitude of the location'),
        validators=[MinValueValidator(-180.0000000), MaxValueValidator(180.0000000)],
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'location'
        verbose_name = 'location'
        verbose_name_plural = _('locations')
        unique_together = ('city', 'name')

    def __str__(self):
        return f"{self.city} - {self.name}"


class Type(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('The name of the type'),
        max_length=100,
        unique=True
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
        help_text=_("The name of the person who contacted"),
        unique=True
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
        blank=True,
        unique=True
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
        help_text=_('The phone number of the provider'),
        unique=True
    )
    email = models.EmailField(
        verbose_name=_('email'),
        null=True,
        blank=True,
        max_length=100,
        unique=True
    )
    company_name = models.CharField(
        verbose_name=_('company name'),
        null=True,
        blank=True,
        max_length=100,
        unique=True
    )
    vat_number = models.CharField(
        verbose_name=_('vat number'),
        null=True,
        blank=True,
        max_length=100,
        unique=True
    )

    class Meta:
        db_table = 'provider'
        verbose_name = 'provider'
        verbose_name_plural = _('providers')
        unique_together = ('first_name', 'last_name')

    def nominativo(self):
        return f"{self.first_name} {self.last_name}"

    nominativo.short_description = _('fullname')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Item(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
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
        max_length=100,
        unique=True
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

    def clean(self):
        ecs = ExpenseCategory.objects.filter(parent=self.parent)
        for ec in ecs:
            if ec.code == self.code:
                raise forms.ValidationError({'code': [_(f"Code already in use for ExpenseCategory '{ec.name}'.")]})

    def __str__(self):
        return f"{self.name}"


class Event(TimeStampedModel):
    start_date = models.DateTimeField(
        verbose_name=_('start time'),
        default=timezone.now,
        help_text=_('On what day and at what time the event starts')
    )
    end_date = models.DateTimeField(
        verbose_name=_('end time'),
        default=timezone.now() + timedelta(hours=2),
        help_text=_('On what day and at what time the event ends')
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

    @cached_property
    def consumption(self):
        props = settings.SM_SETTINGS["CONSUMPTIONS"]
        cons = 5 * math.ceil(((decimal.Decimal(self.distance)/props["KM_PER_LITER"])*props["COST_PER_LITER"]*decimal.Decimal(1.1))/5)
        return cons

    @cached_property
    def gross(self):
        return (self.agents.count() * self.payment.amount) + self.extra.amount + self.busker.amount

    def get_payment(self, properties):
        pay = 5 * round((self.payment.amount * max(
                    properties["MIN"],
                    min(
                        decimal.Decimal(math.floor((self.payment.amount * properties["DECREMENT"] + properties["SHOT"])*250)/250),
                        properties["MAX"]
                    )
                ))/5)
        return pay

    @cached_property
    def member_payment(self):
        for agent in self.agents.all():
            group_names = list(agent.groups.values_list('name', flat=True))
            if "Member" in group_names:
                return self.get_payment(settings.SM_SETTINGS["PAYMENTS"]["MEMBER"])
        return 0

    @cached_property
    def viewer_payment(self):
        for agent in self.agents.all():
            group_names = list(agent.groups.values_list('name', flat=True))
            if "Viewer" in group_names:
                return self.get_payment(settings.SM_SETTINGS["PAYMENTS"]["VIEWER"])
        return 0

    @cached_property
    def total_expenses(self):
        return Expense.objects.filter(event=self).aggregate(Sum('amount'))['amount__sum'] or 0

    def agents_cost(self):
        member_agents = 0
        for agent in self.agents.all():
            group_names = list(agent.groups.values_list('name', flat=True))
            if "Member" in group_names:
                member_agents += 1
        member_cost = member_agents * self.member_payment
        viewer_cost = (self.agents.count() - member_agents) * self.viewer_payment
        return [member_cost, viewer_cost]

    @cached_property
    def agency_percentage(self):
        real_busker = 0 if self.provider is None else self.busker.amount
        costs = self.agents_cost()
        return self.gross - real_busker - costs[0] - costs[1] - self.extra.amount

    @cached_property
    def net(self):
        if self.payment.amount is None:
            return self.busker.amount - self.total_expenses
        costs = self.agents_cost()
        return self.gross - costs[0] - costs[1] - self.total_expenses

    @cached_property
    def cash_fund(self):
        return 0

    class Meta:
        db_table = 'event'
        verbose_name = 'event'
        verbose_name_plural = _('events')

    def clean(self):
        if self.end_date < self.start_date:
            raise forms.ValidationError({'end_date': ["End date should be greater than start date."]})

    def __str__(self):
        return f"{self.start_date:%d/%m/%Y} | {self.location} | {self.type}"


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
        default=False,
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

    def clean(self):
        event = self.event
        if event:
            self.date = event.end_date

    def __str__(self):
        return f"{self.date:%d/%m/%Y}"


class Setting(TimeStampedModel):
    name = models.CharField(
        verbose_name=_('name'),
        help_text=_('The name of the setting'),
        max_length=100
    )
    value = models.CharField(
        verbose_name=_('value'),
        help_text=_('The value of the setting. This value is stored as a string for compliance purpose'),
        max_length=500
    )
    value_type = models.CharField(
        verbose_name=_('Type'),
        help_text=_('The type of the setting'),
        max_length=1,
        choices=(('s', 'string'), ('i', 'integer'), ('b', 'boolean'), ('f', 'float')),
        default='s'
    )
    description = models.TextField(
        verbose_name=_('description'),
        help_text=_('The description of the setting'),
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'setting'
        verbose_name = 'setting'
        verbose_name_plural = _('settings')

    def actual_value(self):
        types = {
            's': str,
            'i': int,
            'b': (lambda v: v.lower().startswith('t') or v.startswith('1')),
            'f': float
        }
        return types[self.value_type](self.value)

    def __str__(self):
        return f"{self.name}"

