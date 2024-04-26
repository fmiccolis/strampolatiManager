import datetime
import json
import calendar
import logging

from django.db.models import Sum
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.utils import timezone
from djmoney.money import Money

from api.models import Event, Expense

logger = logging.getLogger("custom")


class HomeView(RedirectView):
    pattern_name = "admin:index"


def ymdToFilter(y, m, d, param) -> dict:
    instance_filter = dict()
    if y is not None:
        instance_filter[f'{param}__year'] = y
    if m is not None:
        instance_filter[f'{param}__month'] = m
    if d is not None:
        instance_filter[f'{param}__day'] = d
    return instance_filter


def dashboard_callback(request, context):
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    start = Event.objects.earliest('start_date').start_date
    now = timezone.now()

    events = Event.objects.all()
    expenses = Expense.objects.all()
    keys = [[int(start.year + y), None, None] for y in range(0, now.year - start.year + 1)]
    table_headers = ["Anno", "Entrate", "Costi esterni", "Valore aggiunto", "Stipendi", "Ebitda", "Ammortamenti e svalutazioni", "Ebit", "Fondo cassa"]
    periodicity = "years"
    subtitle = None
    if year is not None:
        events = events.filter(start_date__year=year)
        expenses = expenses.filter(date__year=year)
        keys = [[int(year), int(da), None] for da in range(1, 13)]
        table_headers[0] = "Mese"
        periodicity = "months"
        subtitle = year
        if month is not None:
            events = events.filter(start_date__month=month)
            expenses = expenses.filter(date__month=month)
            keys = [[int(year), int(month), int(day)] for day in range(1, calendar.monthrange(int(year), int(month))[1]+1)]
            table_headers[0] = "Data"
            periodicity = "days"
            subtitle = datetime.date(int(year), int(month), 1).strftime("%B %Y")

    period_earnings = sum([evt.gross for evt in events])
    period_costs = sum([exp.amount.amount for exp in expenses.filter(depreciable=False)])
    period_viewer_costs = sum([evt.agents_cost()[1] for evt in events])
    period_external_costs = period_costs + period_viewer_costs
    period_events = events.count()
    period_cash_fund = events.latest("start_date").cash_fund
    kpi = [
        {
            "title": "Ricavi totali",
            "metric": Money(period_earnings, "EUR"),
            "footer": mark_safe(
                '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
            )
        },
        {
            "title": "Uscite totali",
            "metric": Money(period_external_costs, "EUR"),
            "footer": mark_safe(
                '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
            )
        },
        {
            "title": "Eventi totali",
            "metric": period_events,
            "footer": mark_safe(
                '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
            )
        },
        {
            "title": "Fondo cassa",
            "metric": Money(period_cash_fund, "EUR"),
            "footer": mark_safe(
                '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
            )
        }
    ]

    positive = list()
    negative = list()
    average_percentage = list()
    average = list()
    max_gross = 0
    labels = list()
    participation = dict()
    progress = list()
    max_num = 0
    table_content = list()
    for [year, month, day] in keys:
        label = year
        if month is not None:
            label_date = datetime.date(year, month, 1)
            label_format = "%B %Y"
            if day is not None:
                label_date = datetime.date(year, month, day)
                label_format = "%d %B %Y"
            label = label_date.strftime(label_format)
        labels.append(label)
        event_filter = ymdToFilter(year, month, day, "start_date")
        events_in_comb = events.filter(**event_filter)
        expense_filter = ymdToFilter(year, month, day, "date")
        expenses_in_comb = expenses.filter(**expense_filter)
        expenses_not_depreciable = expenses_in_comb.filter(depreciable=False)
        expenses_depreciable = expenses_in_comb.filter(depreciable=True)
        gross = 0
        exp = 0
        paychecks = 0
        for event in events_in_comb:
            gross += float(event.gross)
            exp += float(event.agents_cost()[1])
            paychecks += float(event.agents_cost()[0])
            for agent in event.agents.all():
                exists = participation.get(agent.nominativo(), None)
                if exists is None:
                    participation[agent.nominativo()] = 0
                participation[agent.nominativo()] += 1
                max_num = max(max_num, participation[agent.nominativo()])
        for expense in expenses_not_depreciable:
            exp += float(expense.amount.amount)
        max_gross = max(max_gross, gross)
        positive.append(gross)
        negative.append(-exp)
        average_percentage.append((1 - (exp / gross)) * 100 if gross != 0 else 0)
        added_value = gross - exp
        ebitda = added_value - paychecks
        ammor = float(expenses_depreciable.aggregate(Sum('amount'))['amount__sum'] or 0) / 5
        ebit = ebitda - ammor
        if expenses_in_comb.count() > 0 or events_in_comb.count() > 0:
            table_content.append({
                "link": f"?year={year}{'&month=' + str(month) if month is not None else ''}",
                "key": str(label),
                "gross": gross,
                "external_cost": exp,
                "added_value": added_value,
                "paychecks": paychecks,
                "ebitda": ebitda,
                "ammor": ammor,
                "ebit": ebit,
                "cash_fund": events_in_comb.latest("start_date").cash_fund
            })

    # for perc in average_percentage:
    #    average.append((perc * max_gross) / 100)

    for key, value in participation.items():
        progress.append({
            "title": key,
            "description": value,
            "value": round((100 * value) / max_num)
        })

    context.update({
        "subtitle": subtitle,
        "navigation": [
            {"title": _("Dashboard"), "link": "/", "active": True},
            {"title": _("Metrics"), "link": "#"},
            {"title": _("Settings"), "link": reverse("admin:api_setting_changelist")},
        ],
        "filters": [
            {"title": _("All"), "link": "#", "active": True},
            {
                "title": _("New"),
                "link": reverse("admin:api_event_add"),
            },
        ],
        "kpi": kpi,
        "progress": progress,
        "chart": {
            "settings": {
                "title": _(f"Earnings and expenses in the last {len(positive)} {periodicity}")
            },
            "data": json.dumps({
                "labels": labels,
                "datasets": [
                    {
                        "label": "Percentuale valore aggiunto",
                        "type": "line",
                        "data": average,
                        "backgroundColor": "#f0abfc",
                        "borderColor": "#f0abfc",
                    },
                    {
                        "label": "Entrate",
                        "data": positive,
                        "backgroundColor": "#9333ea",
                    },
                    {
                        "label": "Uscite",
                        "data": negative,
                        "backgroundColor": "#f43f5e",
                    },
                ],
            })
        },
        "performance": [
            {
                "title": _(f"Best grossing {periodicity}"),
                "metric": max(table_content, key=lambda x: x['gross']),
                "param": "gross",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [year['key'] for year in table_content],
                        "datasets": [
                            {
                                "data": [float(cont['gross']) for cont in table_content],
                                "borderColor": "#f43f5e",
                                "backgroundColor": "#9333ea"
                            }
                        ],
                    }
                ),
            },
            {
                "title": _(f"Worst expense {periodicity}"),
                "metric": max(table_content, key=lambda x: x['external_cost']),
                "param": "external_cost",
                "footer": mark_safe(
                    '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                ),
                "chart": json.dumps(
                    {
                        "labels": [year['key'] for year in table_content],
                        "datasets": [
                            {
                                "data": [float(cont['external_cost']) for cont in table_content],
                                "borderColor": "#9333ea",
                                "backgroundColor": "#f43f5e"
                            }
                        ],
                    }
                ),
            },
        ],
        "table_headers": table_headers,
        "table_content": table_content
    })

    return context
