import datetime
import json
import random
import logging
from collections import OrderedDict
from decimal import Decimal

from django.db.models import Count, Sum, F, ExpressionWrapper, FloatField, Min
from django.db.models.functions.datetime import ExtractMonth, ExtractYear, ExtractDay, TruncDate
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.utils import timezone

from api.models import Event, Expense

logger = logging.getLogger("custom")


class HomeView(RedirectView):
    pattern_name = "admin:index"


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
    for comb in combinations:
        events_in_comb = Event.objects.filter(start_date__year=comb["year"])
        expenses_in_comb = Expense.objects.filter(date__year=comb["year"])
        if comb.get("month", None) is not None:
            events_in_comb = events_in_comb.filter(start_date__month=comb["month"])
            expenses_in_comb = expenses_in_comb.filter(date__month=comb["month"])
        if events_in_comb.exists():
            paid_events = events_in_comb.exclude(paid=None)
            before_today = events_in_comb.filter(start_date__lte=now)
            after_today = events_in_comb.filter(start_date__gt=now)




            count = events_in_comb.count()
            dones = events_in_comb.filter(start_date__lte=now).count()
            to_dos = count - dones
            money_make = sum([raw["g"] for raw in events_in_comb.annotate(g=(F('payment') * Count('agents')) + F('busker') + F('extra')).values('g')])
            in_the_period_expenses = expenses_in_comb.filter(depreciable=False).aggregate(Sum('amount'))['amount__sum'] or 0
            viewer_expenses = sum([raw.agents_cost()[1] for raw in events_in_comb])
            external_costs = in_the_period_expenses + viewer_expenses
            added_value = money_make - external_costs
            paychecks = sum([raw.agents_cost()[0] for raw in events_in_comb])
            ebitda = added_value - paychecks
            ammor = (expenses_in_comb.filter(depreciable=True).aggregate(Sum('amount'))['amount__sum'] or 0)/Decimal(5)
            ebit = ebitda - ammor
            final_cash_fund = 0

            table_content.append({
                "key": (datetime.date(1900, int(comb["month"]), 1).strftime('%B') if comb.get("month", None) is not None else "") + " " + comb.get("year"),
                "gross": money_make,
                "external_cost": external_costs,
                "added_value": added_value,
                "paychecks": paychecks,
                "ebitda": ebitda,
                "ammor": ammor,
                "ebit": ebit,
                "cash_fund": final_cash_fund
            })

    context.update(
        {
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
