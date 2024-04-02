from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import Sum
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
from unfold.forms import AdminPasswordChangeForm, UserCreationForm
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from api.models import User, Location, Type, ExpenseCategory, Item, Contact, Provider, Event, Expense, Note

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
    fields = ['date', 'location', 'type', 'provider', 'contact']
    readonly_fields = ['date', 'location', 'type', 'provider', 'contact']
    can_delete = False


class ExpenseInline(StackedInline):
    model = Expense
    max_num = 3
    extra = 0


class NoteInline(StackedInline):
    model = Note
    max_num = 3
    extra = 0


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
    list_display = ('display_header', 'propic', 'group')
    change_password_form = AdminPasswordChangeForm
    add_form = UserCreationForm
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def propic(self, user: User):
        if user.profile_pic:
            return mark_safe(f'<a href="{settings.MEDIA_URL}{user.profile_pic}" target="_blank">vedi foto</a>')

    propic.short_description = "immagine profilo"

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
        return [instance.nominativo(), instance.email, initials]


class LocationAdmin(ModelAdmin):
    fieldsets = [
        (None, {'fields': [('city', 'name')]}),
        (_('Coordinates'), {'fields': (('latitude', 'longitude'), 'show_map')})
    ]
    list_display = ('city', 'name', 'go_on_maps')
    list_filter = ('city', 'name')
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
    list_display = ('name', 'quantity', 'item_image')
    list_filter = ('quantity',)

    def item_image(self, item: Item):
        if item.image:
            return mark_safe(f'<a href="{settings.MEDIA_URL}{item.image}" target="_blank">vedi immagine</a>')

    item_image.short_description = "immagine"


class ContactAdmin(ModelAdmin):
    fieldsets = (
        (_('First Information'), {'fields': (('first_contact', 'full_name', 'phone'),)}),
        (_('Event Information'), {'fields': (('event_date', 'confirm_date'), 'additional_info')}),
    )
    list_display = ('full_name', 'phone', 'event_date', 'beauty_content')
    inlines = [EventsInline]
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }

    def beauty_content(self, instance: Contact):
        return mark_safe(instance.additional_info)
    beauty_content.short_description = "Info"


class TypeAdmin(ModelAdmin):
    inlines = [EventsInline]
    formfield_overrides = {
        django_models.TextField: {
            "widget": WysiwygWidget,
        }
    }


class ExpenseCategoryAdmin(ModelAdmin):
    fieldsets = (
        (None, {'fields': (('name', 'code'), 'parent')}),
    )


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
    list_display = ('nominativo', 'phone', 'propic')
    inlines = [EventsInline]

    def propic(self, provider: Provider):
        if provider.profile_pic:
            return mark_safe(f'<a href="{settings.MEDIA_URL}{provider.profile_pic}" target="_blank">vedi foto</a>')

    propic.short_description = "immagine profilo"


class EventAdmin(ModelAdmin):
    fieldsets = (
        (_('Time info'), {'fields': (('date', 'start_time', 'end_time'),)}),
        (_('Location info'), {'fields': (('distance', 'location'),)}),
        (_('Type and people info'), {'fields': (('type', 'contact', 'provider'),)}),
        (_('Payment info'), {'fields': ('agents', ('payment', 'extra', 'busker'),)}),
        (_('Invoice info'), {'fields': (('sent', 'paid'),)}),
    )
    list_filter = [
        # ("date", RangeNumericFilter),
        # ("laps", SingleNumericFilter),
        ("date", RangeDateFilter),
        "location",
        "type",
        "contact",
        "provider",
        "agents"
    ]
    filter_horizontal = ('agents',)
    list_display = ('display_header', 'provider', 'gross', 'list_agents', 'total_expenses', 'has_notes', 'status')
    ordering = ('-date',)
    inlines = [ExpenseInline, NoteInline]

    def gross(self, event: Event):
        if event.agents.count() > 0:
            return Money((event.agents.count() * event.payment.amount) + event.extra.amount + event.busker.amount, 'EUR')
    gross.short_description = "Lordo"

    def list_agents(self, event: Event):
        if event.agents.count() > 0:
            return ", ".join([agent.first_name for agent in event.agents.all()])
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
        return [instance.date, f"{instance.type} | {instance.location}"]

    def total_expenses(self, instance: Event):
        return Money(Expense.objects.filter(event=instance).aggregate(Sum('amount'))['amount__sum'] or 0, "EUR")
    total_expenses.short_description = "Spese"

    def has_notes(self, instance: Event):
        if Note.objects.filter(event=instance).count() > 0:
            return mark_safe(f"<a href='{reverse("admin:api_note_changelist")}?event__id__exact={instance.pk}'><span class='material-symbols-outlined md-18 mr-3 w-4.5'>note</span></a>")
        return None
    has_notes.short_description = "Note"


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
