import datetime
import decimal
import math
from typing import Any
import logging

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import Sum, Model, Max
from django.forms import Form, ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_celery_beat.models import PeriodicTask, IntervalSchedule, SolarSchedule, ClockedSchedule, CrontabSchedule
from djmoney.money import Money
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import GroupAdmin
from django.utils.safestring import mark_safe
from django.db import models as django_models
from rest_framework_simplejwt.token_blacklist import models
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from django.utils.translation import gettext, gettext_lazy as _
from unfold.contrib.filters.admin import RangeNumericFilter, SingleNumericFilter, RangeDateFilter
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from api.models import User, Location, Type, ExpenseCategory, Item, Contact, Provider, Event, Expense, Note, Setting

logger = logging.getLogger("custom")

# Register your models here.
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(Group)


class EventsInline(TabularInline):
    model = Event
    extra = 0
    fields = ['start_date', 'location', 'type', 'provider', 'contact']
    readonly_fields = ['start_date', 'location', 'type', 'provider', 'contact']
    can_delete = False


class ParticipationInline(TabularInline):
    model = Event.agents.through
    extra = 0


class ExpenseInline(StackedInline):
    model = Expense
    max_num = 3
    extra = 0
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }


class NoteInline(StackedInline):
    model = Note
    max_num = 3
    extra = 0
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }


class CustomUserAdmin(UserAdmin, ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'profile_pic')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    change_password_form = AdminPasswordChangeForm
    add_form = UserCreationForm
    form = UserChangeForm
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    inlines = [ParticipationInline]

    def get_list_display(self, request):
        base_list = ('display_header', 'event_total')
        if request.user.is_superuser or request.user.groups.filter(name__exact="Member").exists():
            base_list += ('earnings',)
        base_list += ('group',)
        return base_list

    def event_total(self, user: User):
        now = datetime.datetime.now()
        dones = Event.objects.filter(agents__id__exact=user.pk, start_date__lt=now).count()
        to_do = Event.objects.filter(agents__id__exact=user.pk, start_date__gte=now).count()
        id_filter = f"agents__id__exact={user.pk}"
        dlt_filter = f"start_date__lt={now:%Y-%m-%d}"
        dgte_filter = f"start_date__gte={now:%Y-%m-%d}"
        return mark_safe(
            f"<a href='{reverse("admin:api_event_changelist")}?{id_filter}&{dlt_filter}'>{dones}</a> "
            f"(<a href='{reverse("admin:api_event_changelist")}?{id_filter}&{dgte_filter}'>{to_do}</a>)"
            if user.groups.filter(name__in=['Member', 'Viewer']).exists() else ""
        )

    event_total.short_description = "Totale eventi"

    def earnings(self, user: User):
        total_earnings = None
        events = Event.objects.filter(agents__email=user.email, paid__isnull=False)
        p_settings = settings.SM_SETTINGS["PAYMENTS"]
        if events.exists():
            if user.groups.filter(name__exact="Member").exists():
                sett = p_settings["MEMBER"]
                total_earnings = 0
            elif user.groups.filter(name__exact="Viewer").exists():
                sett = p_settings["VIEWER"]
                total_earnings = 0
            else:
                return ""

            for evt in events:
                total_earnings += 5 * round((evt.payment.amount * max(
                    sett["MIN"],
                    min(
                        decimal.Decimal(math.floor((evt.payment.amount * sett["DECREMENT"] + sett["SHOT"])*250)/250),
                        sett["MAX"]
                    )
                ))/5)
        return Money(total_earnings, "EUR") if total_earnings else ""

    earnings.short_description = "Guadagni"

    @display(
        description=_("Role"),
        ordering="inner_role",
        label={
            "Member": "success",
            "Viewer": "warning"
        }
    )
    def group(self, user: User):
        if user.groups.count() > 0:
            return f"{user.groups.first()}"

    group.short_description = "Ruolo"

    @display(description=_("Agent"), header=True)
    def display_header(self, instance: User):
        initials = f"{instance.first_name[0]}{instance.last_name[0]}" if instance.first_name and instance.last_name else "AB"
        return [instance.nominativo(), instance.email, mark_safe(f"<img src='/{instance.profile_pic}' style='height:100%;object-fit:cover' alt='damn' />") if instance.profile_pic else initials]


class LocationAdmin(ModelAdmin):
    fieldsets = [
        (None, {'fields': [('city', 'name')]}),
        (_('Coordinates'), {'fields': (('latitude', 'longitude'), 'show_map')})
    ]
    list_display = ('city', 'name', 'go_on_maps')
    list_filter = ('city', 'name')
    ordering = ('city','name')
    readonly_fields = ('show_map',)
    inlines = [EventsInline]

    class Media:
        js = ('map/ol.js',)
        css = {"all": ('map/ol.css',)}

    def go_on_maps(self, location: Location):
        if location.longitude and location.latitude:
            return mark_safe(
                f'<a href="https://maps.google.com/maps?q={location.latitude},{location.longitude}" target="_blank">vai alla mappa</a>')

    go_on_maps.short_description = "vedi su mappa"

    def show_map(self, location: Location):
        jsCode = """
        <div id="demoMap" style="height:250px;width:500px;"></div>
        <script>
            var lat = """ + str(location.latitude if location.latitude else "40.852226") + """;
            var lon = """ + str(location.longitude if location.longitude else "17.118713") + """;
            var loc = ol.proj.transform([lon, lat], "EPSG:4326", "EPSG:3857")
        
            const iconFeature = new ol.Feature({
              geometry: new ol.geom.Point(loc),
              name: 'Null Island',
              population: 4000,
              rainfall: 500,
            });
            
            const iconStyle = new ol.style.Style({
              image: new ol.style.Icon({
                anchor: [0.5, 46],
                anchorXUnits: 'fraction',
                anchorYUnits: 'pixels',
                src: '/static/map/images/marker-icon.png',
              }),
            });
            
            iconFeature.setStyle(iconStyle);
            
            const vectorSource = new ol.source.Vector({
              features: [iconFeature],
            });
            
            const vectorLayer = new ol.layer.Vector({
              source: vectorSource,
            });
            
            const rasterLayer = new ol.layer.Tile({
              source: new ol.source.OSM(),
            });
            
            const map = new ol.Map({
              layers: [rasterLayer, vectorLayer],
              target: document.getElementById('demoMap'),
              view: new ol.View({
                center: loc,
                zoom: 18,
              }),
            });
            
            map.on('singleclick', function (evt) {
                var updated = ol.proj.transform(evt.coordinate, "EPSG:3857", "EPSG:4326")
                document.getElementById("id_longitude").value = updated[0];
                document.getElementById("id_latitude").value = updated[1];
                
                iconFeature.setGeometry(new ol.geom.Point(evt.coordinate));
            });
        </script>"""

        return mark_safe(jsCode)


class ItemAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': (('name', 'quantity'), 'image')}),
    )
    list_display = ('item_image', 'name', 'quantity')
    list_filter = [('quantity', RangeNumericFilter), ]
    list_filter_submit = True
    list_editable = ('quantity',)

    @display(description=_("Image"), header=True)
    def item_image(self, item: Item):
        src = f"{settings.STATIC_URL}/images/defaults/item_default.jpg"
        if item.image:
            src = f"{settings.MEDIA_URL}{item.image}"
        return [mark_safe(f'<img src="{src}" style="width:clamp(100px,10vw,300px)" alt="damn" />')]


class ContactAdmin(ModelAdmin):
    fieldsets = (
        (_('First Information'), {'fields': (('first_contact', 'full_name', 'phone'),)}),
        (_('Event Information'), {'fields': (('event_date', 'confirm_date'), 'additional_info')}),
    )
    list_display = ('full_name', 'phone', 'event_date', 'beauty_content', 'status')
    inlines = [EventsInline]
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    def beauty_content(self, instance: Contact):
        return mark_safe(instance.additional_info)
    beauty_content.short_description = "Info"

    @display(
        description=_("Status"),
        ordering="status",
        label={
            "Perso": "danger",
            "Confermabile": "warning",
            "Confermato": "success",
        }
    )
    def status(self, instance: Contact):
        current_status = "Perso"
        if instance.event_date is None or instance.event_date > datetime.date.today():
            current_status = "Confermabile"
        if instance.confirm_date is not None:
            current_status = "Confermato"
        return current_status
    status.short_description = _("Status")


class TypeAdmin(ModelAdmin):
    inlines = [EventsInline]
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    list_display = ('name', 'beauty_description')

    def beauty_description(self, instance: Type):
        return mark_safe(instance.description)
    beauty_description.short_description = _("Description")


class ExpenseCategoryAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': (('name', 'code'), 'parent')}),
    )
    list_display = ('name', 'compute_code', 'parent')

    def compute_code(self, instance: ExpenseCategory):
        parent = instance.parent
        final_code = ""
        if parent:
            final_code += self.compute_code(parent)
        return final_code + instance.code
    compute_code.short_description = _("Code")


class NoteAdmin(ModelAdmin):
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    list_filter = ('event',)
    list_display = ('date', 'is_event', 'beauty_content')

    def is_event(self, instance: Note):
        return mark_safe("<span class='material-symbols-outlined md-18 mr-3 w-4.5'>check</span>") if instance.event else None
    is_event.short_description = "Evento?"

    def beauty_content(self, instance: Note):
        return mark_safe(instance.content)
    beauty_content.short_description = "Content"


class ExpenseAdmin(ModelAdmin):
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    list_filter = ('event',)
    list_display = ('date', 'is_event', 'beauty_content')

    def is_event(self, instance: Expense):
        return mark_safe("<span class='material-symbols-outlined md-18 mr-3 w-4.5'>check</span>") if instance.event else None
    is_event.short_description = "Evento?"

    def beauty_content(self, instance: Expense):
        return mark_safe(instance.description)
    beauty_content.short_description = "Description"


class ProviderAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': (('first_name', 'last_name'),)}),
        (_('Personal info'), {'fields': (('email', 'phone'), 'profile_pic')}),
        (_('Company info'), {'fields': (('company_name', 'vat_number'),)}),
    )
    list_display = ('propic', 'nominativo', 'call_phone')
    inlines = [EventsInline]

    @display(description=_(""), header=True)
    def propic(self, item: Provider):
        src = f"{settings.STATIC_URL}/images/defaults/person_default.jpg"
        if item.profile_pic:
            src = f"{settings.MEDIA_URL}{item.profile_pic}"
        return [mark_safe(f'<img src="{src}" style="width:clamp(100px,10vw,300px)" alt="damn" />')]

    def call_phone(self, instance: Provider):
        return mark_safe(f"<a href='tel:{instance.phone}'><span class='material-symbols-outlined md-18 mr-3 w-4.5'>phone</span>&nbsp;{instance.phone}</a>")
    call_phone.short_description = _("Phone")


class EventAdmin(ModelAdmin):
    fieldsets = (
        (_('Time info'), {'classes': ["tab"], 'fields': ('start_date', 'end_date',)}),
        (_('Location info'), {'classes': ["tab"], 'fields': (('distance', 'location'),)}),
        (_('Type and people info'), {'classes': ["tab"], 'fields': (('type', 'contact', 'provider'),)}),
        (_('Payment info'), {'classes': ["tab"], 'fields': ('agents', ('payment', 'extra', 'busker'),)}),
        (_('Invoice info'), {'classes': ["tab"], 'fields': (('sent', 'paid'),)}),
    )
    list_filter = [
        # ("date", RangeNumericFilter),
        # ("laps", SingleNumericFilter),
        ("start_date", RangeDateFilter),
        "location",
        "type",
        "contact",
        "provider",
        "agents"
    ]
    list_filter_submit = True
    filter_horizontal = ('agents',)
    list_display = ('display_header', 'distance', 'consumption', 'provider', 'payment', 'extra', 'busker', 'gross', 'list_agents', 'total_expenses', 'has_notes', 'status')
    ordering = ('-start_date',)
    inlines = [ExpenseInline, NoteInline]

    def list_agents(self, event: Event):
        links = []
        agents = event.agents
        if agents.count() > 0:
            for agent in agents.all():
                links.append(f"<a href='{reverse("admin:api_user_change", kwargs={'object_id': agent.pk})}'>{agent.first_name}</a>")
        return mark_safe(", ".join(links))
    list_agents.short_description = "Agenti"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "agents":
            agents = User.objects.filter(groups__name__in=['Member', 'Viewer'])
            kwargs["queryset"] = agents
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @display(
        description=_("Status"),
        ordering="status",
        label={
            "Non inviato": "gray",
            "Inviato": "warning",
            "Pagato": "success",
        }
    )
    def status(self, event: Event):
        current_status = "Non inviato"
        if event.sent:
            current_status = "Inviato"
        if event.paid:
            current_status = "Pagato"
        return current_status
    status.short_description = "Stato"

    @display(description=_("Driver"), header=True)
    def display_header(self, instance: Event):
        return [instance.start_date, f"{instance.type} | {instance.location}"]

    def has_notes(self, instance: Event):
        if Note.objects.filter(event=instance).count() > 0:
            return mark_safe(f"<a href='{reverse("admin:api_note_changelist")}?event__id__exact={instance.pk}'><span class='material-symbols-outlined md-18 mr-3 w-4.5'>note</span></a>")
        return None
    has_notes.short_description = "Note"


class SettingAdmin(ModelAdmin):
    fieldsets = [
        (_("Current"), {
            'classes': ["tab"],
            'fields': [
                ('name', 'value_type'), 'value', 'description'
            ],
        }),
        (_("Old"), {
            'classes': ["tab"],
            'fields': [
                ('list_old',),
            ],
            'description': _("Here are stored the old values for this setting")
        }),
    ]
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    readonly_fields = ('list_old',)
    list_display = ('name', 'modified', 'value')
    ordering = ('name',)
    edit_exclude = ('name', 'value_type')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.edit_exclude + self.readonly_fields
        return super().get_readonly_fields(request, obj)

    def get_exclude(self, request, obj=None):
        if obj:
            return self.edit_exclude
        return super().get_exclude(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        max_ids = qs.values('name').annotate(max_id=Max("id")).values_list("max_id", flat=True)
        return qs.filter(pk__in=max_ids)

    def save_model(
        self, request: HttpRequest, obj: Model, form: Form, change: Any
    ) -> None:
        if obj.pk is not None:
            old = Setting.objects.get(pk=obj.pk)
            obj.pk = None if old.value != obj.value else obj.pk

        super().save_model(request, obj, form, change)

    def list_old(self, instance: Setting):
        old_ones = Setting.objects.filter(name=instance.name).exclude(id=instance.id).order_by('-modified')
        htmlCode = f"""
            <div>
                <table class="border border-gray-200 border-spacing-none border-separate mb-6 rounded-md shadow-sm text-gray-700 w-full dark:border-gray-800">
                    <thead class="hidden lg:table-header-group">
                        <tr>
                            <th class="column-start_date align-middle border-b border-gray-200 font-medium px-3 py-2 text-left text-gray-400 text-sm dark:border-gray-800">
                                <span class="flex flex-row items-center">
                                    Date
                                        <span class="cursor-pointer material-symbols-outlined ml-2" title="On what day the setting was modified">help</span>
                                </span>
                            </th>
                            <th class="column-location align-middle border-b border-gray-200 font-medium px-3 py-2 text-left text-gray-400 text-sm dark:border-gray-800">
                                <span class="flex flex-row items-center">
                                    Value
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="original" colspan="10">
                                <p class="align-middle flex font-normal items-center leading-none px-3 text-gray-500 text-left text-sm whitespace-nowrap">
                                </p>
                            </td>
                        </tr>"""

        for old in old_ones:
            htmlCode += f"""
                <tr class="lg:border-b-0 form-row has_original dynamic-event_set" id="event_set-0">
                    <td class="field-start_date p-3 lg:py-3 align-top border-b border-gray-200 flex items-center before:capitalize before:content-[attr(data-label)] before:mr-auto before:text-gray-500 before:w-72 lg:before:hidden font-normal px-3 text-left text-sm lg:table-cell dark:border-gray-800" data-label="date">
                        <p class="bg-gray-50 border font-medium max-w-lg px-3 py-2 rounded-md shadow-sm text-gray-500 text-sm truncate whitespace-nowrap dark:border-gray-700 dark:text-gray-400 dark:bg-gray-800">
                            {old.modified:%A %d %B %Y - %X}
                        </p>
                    </td>
                    <td class="field-location p-3 lg:py-3 align-top border-b border-gray-200 flex items-center before:capitalize before:content-[attr(data-label)] before:mr-auto before:text-gray-500 before:w-72 lg:before:hidden font-normal px-3 text-left text-sm lg:table-cell dark:border-gray-800" data-label="value">
                        <p class="bg-gray-50 border font-medium max-w-lg px-3 py-2 rounded-md shadow-sm text-gray-500 text-sm truncate whitespace-nowrap dark:border-gray-700 dark:text-gray-400 dark:bg-gray-800">
                            {old.value}
                        </p>
                    </td>
                </tr>
            """

        htmlCode += """</tbody></table></div>"""
        return mark_safe(htmlCode)
    list_old.custom_value = "Ehi"


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return True  # or whatever logic you want


@admin.register(Group)
class GroupAdmin(GroupAdmin, ModelAdmin):
    pass


@admin.register(PeriodicTask)
class PeriodicTaskAdmin(ModelAdmin):
    pass


@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass


@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(ModelAdmin):
    pass


@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass


@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(ModelAdmin):
    pass


admin.site.unregister(models.OutstandingToken)
admin.site.register(models.OutstandingToken, CustomOutstandingTokenAdmin)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(ExpenseCategory, ExpenseCategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(Setting, SettingAdmin)
