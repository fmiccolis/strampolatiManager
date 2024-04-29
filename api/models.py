from decimal import Decimal, ROUND_HALF_UP
import math
from datetime import datetime, timedelta
import logging

from django import forms
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Sum, Max
from django.utils.functional import cached_property
from django.utils.translation import gettext, gettext_lazy as _
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from djmoney.models.fields import MoneyField

logger = logging.getLogger("custom")

ITALIAN_PROVINCES = (
    ('AG', 'Agrigento'),
    ('AL', 'Alessandria'),
    ('AN', 'Ancona'),
    ('AO', 'Aosta'),
    ('AP', 'Ascoli-Piceno'),
    ('AQ', 'L’Aquila'),
    ('AR', 'Arezzo'),
    ('AT', 'Asti'),
    ('AV', 'Avellino'),
    ('BA', 'Bari'),
    ('BG', 'Bergamo'),
    ('BI', 'Biella'),
    ('BL', 'Belluno'),
    ('BN', 'Benevento'),
    ('BO', 'Bologna'),
    ('BR', 'Brindisi'),
    ('BS', 'Brescia'),
    ('BT', 'Barletta-Andria-Trani'),
    ('BZ', 'Bolzano'),
    ('CA', 'Cagliari'),
    ('CB', 'Campobasso'),
    ('CE', 'Caserta'),
    ('CH', 'Chieti'),
    ('CI', 'Carbonia Iglesias'),
    ('CL', 'Caltanissetta'),
    ('CN', 'Cuneo'),
    ('CO', 'Como'),
    ('CR', 'Cremona'),
    ('CS', 'Cosenza'),
    ('CT', 'Catania'),
    ('CZ', 'Catanzaro'),
    ('EN', 'Enna'),
    ('FC', 'Forli-Cesena'),
    ('FE', 'Ferrara'),
    ('FG', 'Foggia'),
    ('FI', 'Firenze'),
    ('FM', 'Fermo'),
    ('FR', 'Frosinone'),
    ('GE', 'Genova'),
    ('GO', 'Gorizia'),
    ('GR', 'Grosseto'),
    ('IM', 'Imperia'),
    ('IS', 'Isernia'),
    ('KR', 'Crotone'),
    ('LC', 'Lecco'),
    ('LE', 'Lecce'),
    ('LI', 'Livorno'),
    ('LO', 'Lodi'),
    ('LT', 'Latina'),
    ('LU', 'Lucca'),
    ('MB', 'Monza-Brianza'),
    ('MC', 'Macerata'),
    ('ME', 'Messina'),
    ('MI', 'Milano'),
    ('MN', 'Mantova'),
    ('MO', 'Modena'),
    ('MS', 'Massa-Carrara'),
    ('MT', 'Matera'),
    ('NA', 'Napoli'),
    ('NO', 'Novara'),
    ('NU', 'Nuoro'),
    ('OG', 'Ogliastra'),
    ('OR', 'Oristano'),
    ('OT', 'Olbia Tempio'),
    ('PA', 'Palermo'),
    ('PC', 'Piacenza'),
    ('PD', 'Padova'),
    ('PE', 'Pescara'),
    ('PG', 'Perugia'),
    ('PI', 'Pisa'),
    ('PN', 'Pordenone'),
    ('PO', 'Prato'),
    ('PR', 'Parma'),
    ('PT', 'Pistoia'),
    ('PU', 'Pesaro-Urbino'),
    ('PV', 'Pavia'),
    ('PZ', 'Potenza'),
    ('RA', 'Ravenna'),
    ('RC', 'Reggio-Calabria'),
    ('RE', 'Reggio-Emilia'),
    ('RG', 'Ragusa'),
    ('RI', 'Rieti'),
    ('RN', 'Rimini'),
    ('RO', 'Rovigo'),
    ('Roma', 'Roma'),
    ('SA', 'Salerno'),
    ('SI', 'Siena'),
    ('SO', 'Sondrio'),
    ('SP', 'La-Spezia'),
    ('SR', 'Siracusa'),
    ('SS', 'Sassari'),
    ('SV', 'Savona'),
    ('TA', 'Taranto'),
    ('TE', 'Teramo'),
    ('TN', 'Trento'),
    ('TO', 'Torino'),
    ('TP', 'Trapani'),
    ('TR', 'Terni'),
    ('TS', 'Trieste'),
    ('TV', 'Treviso'),
    ('UD', 'Udine'),
    ('VA', 'Varese'),
    ('VB', 'Verbania'),
    ('VC', 'Vercelli'),
    ('VE', 'Venezia'),
    ('VI', 'Vicenza'),
    ('VR', 'Verona'),
    ('VS', 'Medio Campidano'),
    ('VT', 'Viterbo'),
    ('VV', 'Vibo-Valentia'),
)


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
    province = models.CharField(
        verbose_name=_('province'),
        help_text=_('The province of the city'),
        default="BA",
        choices=ITALIAN_PROVINCES,
        null=True,
        blank=True,
        max_length=4
    )
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
        help_text=_('If valued represent the date the contact confirmed the event')
    )
    cancel_date = models.DateField(
        verbose_name=_('cancel date'),
        null=True,
        blank=True,
        help_text=_('If valued indicate that the event was canceled. In the additional info should be written why')
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
    calendar_id = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    @cached_property
    def get_valid_settings(self):
        this_event_settings_ids = (Setting
                                   .objects
                                   .filter(valid_from__lt=self.start_date)
                                   .values("name")
                                   .annotate(max_id=Max("id"))
                                   .values_list("max_id", flat=True))

        final_list = {}
        for sett in this_event_settings_ids:
            setting = Setting.objects.get(pk=sett)
            final_list[setting.name] = setting.actual_value()

        return final_list

    @cached_property
    def consumption(self):
        setts = self.get_valid_settings
        km_per_liter = Decimal(setts.get("KM_PER_LITER", (100 / 7.5)))
        cost_per_liter = Decimal(setts.get("COST_PER_LITER", 1.801))
        cons = 5 * math.ceil(
            (
                    (Decimal(self.distance) / km_per_liter) *
                    cost_per_liter * Decimal(1.1)
            ) / 5
        )
        return cons

    @cached_property
    def gross(self):
        return (self.agents.count() * self.payment.amount) + self.extra.amount + self.busker.amount

    def get_payment(self, properties):
        if self.provider is None:
            return self.payment
        pay = 5 * Decimal((
            float(self.payment.amount) *
            max(
                properties["MIN"],
                min(
                    math.floor((float(self.payment.amount)*properties["DECREMENT"]+properties["SHOT"])*250)/250,
                    properties["MAX"]
                )
            )
        ) / 5).quantize(0, ROUND_HALF_UP)
        return pay

    @cached_property
    def member_payment(self):
        for agent in self.agents.all():
            group_names = list(agent.groups.values_list('name', flat=True))
            if "Member" in group_names:
                setts = self.get_valid_settings
                return self.get_payment({
                    "MIN": setts.get("MIN_MEMBER_PAYMENT", 0.8),
                    "MAX": setts.get("MAX_MEMBER_PAYMENT", 0.95),
                    "DECREMENT": setts.get("DECREMENT_MEMBER_PAYMENT", (-5 / 3000)),
                    "SHOT": setts.get("SHOT_MEMBER_PAYMENT", (1 + 35 / 300))
                })
        return 0

    @cached_property
    def viewer_payment(self):
        for agent in self.agents.all():
            group_names = list(agent.groups.values_list('name', flat=True))
            if "Viewer" in group_names:
                setts = self.get_valid_settings
                return self.get_payment({
                    "MIN": setts.get("MIN_VIEWER_PAYMENT", 0.7),
                    "MAX": setts.get("MAX_VIEWER_PAYMENT", 0.85),
                    "DECREMENT": setts.get("DECREMENT_VIEWER_PAYMENT", (-5 / 3000)),
                    "SHOT": setts.get("SHOT_VIEWER_PAYMENT", (1 + 5 / 300))
                })
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
        setts = self.get_valid_settings
        initial_cash_fund = Decimal(setts.get("STARTING_CASH_FUND", 0))
        previous_events = Event.objects.filter(start_date__lte=self.start_date).exclude(pk=self.pk)
        previous_events_net = sum([p_evt.net for p_evt in previous_events])
        all_other_expenses = Expense.objects.filter(event__isnull=True, date__lte=self.start_date).aggregate(Sum('amount'))['amount__sum'] or 0
        return initial_cash_fund + self.net + previous_events_net - all_other_expenses

    @cached_property
    def hours_worked(self) -> timedelta:
        return self.end_date - self.start_date

    @cached_property
    def payment_per_hour(self):
        return self.payment.amount/Decimal(self.hours_worked.total_seconds()/60/60)

    @cached_property
    def gross_per_hour(self):
        return self.gross/Decimal(self.hours_worked.total_seconds()/60/60)

    @cached_property
    def pay_time(self):
        if self.sent is None:
            return None
        if self.paid is None:
            return (timezone.now() - self.sent).days
        return (self.paid - self.sent).days

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
        default=timezone.now,
        help_text=_("The date of the expense")
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
        default=timezone.now
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
    valid_from = models.DateTimeField(
        verbose_name=_('valid from'),
        default=timezone.now,
        help_text=_('From which day it starts to be valid')
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
