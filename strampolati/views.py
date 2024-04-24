import datetime
import json
import random
import logging
from collections import OrderedDict
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField, Min
from django.db.models.functions.datetime import ExtractMonth, ExtractYear, ExtractDay, TruncDate
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.utils import timezone
from djmoney.money import Money

from api.models import Event, Expense, User

logger = logging.getLogger("custom")


class HomeView(RedirectView):
    pattern_name = "admin:index"


def getLastXMonths(start_date, months=24) -> []:
    combinations = list()
    first_date = start_date - relativedelta(months=months-1)
    for i in range(months):
        previous_date = first_date + relativedelta(months=i)
        combinations.append([previous_date.month, previous_date.year])
    return combinations


def dashboard_callback(request, context):
    """
    Mi serve:
    - eventi fatti nel periodo (eventi da fare)
    - giorno migliore e quanti soldi fatti in quel giorno
    - pagamento medio socio per evento

    - entrate totali
    - costi esterni
    - valore aggiunto
    - costo degli stipendi
    - EBITDA
    - valore degli ammortamenti e delle svalutazioni
    - EBIT
    - FONDO CASSA
    """

    start = Event.objects.earliest('start_date').start_date
    now = timezone.now()

    combinations = getLastXMonths(now, 24)
    positive = list()
    negative = list()
    average_percentage = list()
    average = list()
    max_gross = 0
    labels = list()
    for [month, year] in combinations:
        labels.append(datetime.date(year, month, 1).strftime("%B %Y"))
        events_in_comb = Event.objects.filter(start_date__month=month, start_date__year=year)
        expenses_in_comb = Expense.objects.filter(date__month=month, date__year=year)
        gross = 0
        expenses = 0
        for event in events_in_comb:
            gross += float(event.gross)
        for expense in expenses_in_comb:
            expenses += float(expense.amount.amount)
        max_gross = max(max_gross, gross)
        positive.append(gross)
        negative.append(-expenses)
        average_percentage.append((1-(expenses/gross))*100 if gross != 0 else 0)

    logger.info(labels)
    for perc in average_percentage:
        average.append((perc*max_gross)/100)

    combinations = list()
    uniques_comb = list()
    for ccc in range((now - start).days):
        [month, year] = (start + datetime.timedelta(ccc)).strftime(r"%m-%Y").split("-")
        if f"{year}" not in uniques_comb:
            uniques_comb.append(f"{year}")
            combinations.append({"year": year})
        if f"{month}|{year}" not in uniques_comb:
            uniques_comb.append(f"{month}|{year}")
            combinations.append({"month": month, "year": year})

    table_content = list()
    total_earnings = 0
    total_costs = 0
    total_events = 0
    for comb in combinations:
        events_in_comb = Event.objects.filter(start_date__year=comb["year"])
        expenses_in_comb = Expense.objects.filter(date__year=comb["year"])
        if comb.get("month", None) is not None:
            events_in_comb = events_in_comb.filter(start_date__month=comb["month"])
            expenses_in_comb = expenses_in_comb.filter(date__month=comb["month"])
        if events_in_comb.exists():
            events_in_comb = events_in_comb.exclude(paid=None)
            before_today = events_in_comb.filter(start_date__lte=now)
            after_today = events_in_comb.filter(start_date__gt=now)

            total_events += events_in_comb.count() if comb.get("month", None) is not None else 0
            count = events_in_comb.count()
            dones = events_in_comb.filter(start_date__lte=now).count()
            to_dos = count - dones
            money_make = sum([raw["g"] for raw in events_in_comb.annotate(
                g=(F('payment') * Count('agents')) + F('busker') + F('extra')).values('g')])
            total_earnings += money_make if comb.get("month", None) is not None else 0
            in_the_period_expenses = expenses_in_comb.filter(depreciable=False).aggregate(Sum('amount'))[
                                         'amount__sum'] or 0
            viewer_expenses = sum([raw.agents_cost()[1] for raw in events_in_comb])
            external_costs = in_the_period_expenses + viewer_expenses
            total_costs += external_costs if comb.get("month", None) is not None else 0
            added_value = money_make - external_costs
            paychecks = sum([raw.agents_cost()[0] for raw in events_in_comb])
            ebitda = added_value - paychecks
            ammor = (expenses_in_comb.filter(depreciable=True).aggregate(Sum('amount'))['amount__sum'] or 0) / Decimal(
                5)
            ebit = ebitda - ammor
            final_cash_fund = 0

            table_content.append({
                "key": (_(datetime.date(1900, int(comb["month"]), 1).strftime('%B')) if comb.get("month",
                                                                                                 None) is not None else "") + " " + comb.get(
                    "year"),
                "gross": money_make,
                "external_cost": external_costs,
                "added_value": added_value,
                "paychecks": paychecks,
                "ebitda": ebitda,
                "ammor": ammor,
                "ebit": ebit,
                "cash_fund": final_cash_fund,
                "display": "none" if comb.get("month", None) is not None else "table-row"
            })

    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    # positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    # negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    # average = [r[1] - random.randint(3, 5) for r in positive]
    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]

    progress = list()
    max_num = 0
    for agent in User.objects.all():
        if agent.groups.count() > 0:
            events_count = Event.objects.filter(agents__in=[agent]).count() or 0
            max_num = max(max_num, events_count)
            progress.append({
                "title": agent.nominativo(),
                "description": f"{events_count}",
                "value": events_count
            })
    for pro in progress:
        raw_value = pro["value"]
        pro["value"] = round((100*raw_value)/max_num)

    context.update(
        {
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
            "kpi": [
                {
                    "title": "Ricavi totali",
                    "metric": Money(total_earnings, 'EUR'),
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
                {
                    "title": "Uscite totali",
                    "metric": Money(total_costs, 'EUR'),
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
                {
                    "title": "Eventi totali",
                    "metric": total_events,
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
                {
                    "title": "Fondo cassa",
                    "metric": Money(0, 'EUR'),
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
            ],
            "progress": progress,
            "chart": {
                "settings": {
                    "title": _(f"Earnings and expenses in the last {len(positive)} months")
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
                    "title": _("Last week revenue"),
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                    "chart": json.dumps(
                        {
                            "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                            "datasets": [
                                {"data": performance_positive, "borderColor": "#9333ea"}
                            ],
                        }
                    ),
                },
                {
                    "title": _("Last week expenses"),
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                    "chart": json.dumps(
                        {
                            "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                            "datasets": [
                                {"data": performance_negative, "borderColor": "#f43f5e"}
                            ],
                        }
                    ),
                },
            ],
            "table_headers": [
                "Anno/Mese",
                "Entrate",
                "Costi esterni",
                "Valore aggiunto",
                "Stipendi",
                "Ebitda",
                "Ammortamenti e svalutazioni",
                "Ebit",
                "Fondo cassa"
            ],
            "table_content": table_content
        },
    )

    return context
