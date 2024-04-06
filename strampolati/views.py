import datetime
import json
import random
import logging

from django.db.models import Count, Sum
from django.db.models.functions.datetime import ExtractMonth, ExtractYear, ExtractDay
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

    events = Event.objects.all().order_by()

    # logger.info(qs)

    events_context = {}
    now = timezone.now()
    for event in events:
        year = f"{event.start_date:%Y}"
        month = f"{event.start_date:%m}"
        day = f"{event.start_date:%d}"
        counter = "to_do"
        if event.start_date <= now:
            counter = "dones"
        gross = (event.payment.amount * event.agents.count()) + event.extra.amount + event.busker.amount
        expense = Expense.objects.filter(event=event).aggregate(Sum('amount'))['amount__sum'] or 0

        if year not in events_context:
            events_context[year] = {
                "dones": 0,
                "to_do": 0,
                "gross": 0,
                "expense": 0,
                "best_day": {}
            }

        this_year_context = events_context.get(year, None)

        if month not in this_year_context:
            this_year_context[month] = {
                "dones": 0,
                "to_do": 0,
                "gross": 0,
                "expense": 0,
                "best_day": {
                    "date": "",
                    "import": 0
                }
            }
        this_month_context = this_year_context.get(month, None)

        this_month_context[counter] += 1
        this_month_context["gross"] += gross
        this_month_context["expense"] += expense
        this_year_context[counter] += 1
        this_year_context["gross"] += gross
        this_year_context["expense"] += expense

        # calcolo il giorno migliore per il mese
        max_payment_day = Event.objects.annotate(
            day=ExtractDay('start_date')
        ).values('day').annotate(
            total_payment=Sum('payment')
        ).order_by('-total_payment').first()
        logger.info(max_payment_day)



    logger.info(events_context)

    WEEKDAYS = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]

    positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]
    average = [r[1] - random.randint(3, 5) for r in positive]
    performance_positive = [[1, random.randrange(8, 28)] for i in range(1, 28)]
    performance_negative = [[-1, -random.randrange(8, 28)] for i in range(1, 28)]

    context.update(
        {
            "navigation": [
                {"title": _("Dashboard"), "link": "/", "active": True},
                {"title": _("Analytics"), "link": "#"},
                {"title": _("Settings"), "link": "#"},
            ],
            "filters": [
                {
                    "title": _("All"),
                    "link": "#",
                    "active": True
                },
                {
                    "title": _("New"),
                    "link": "#",
                },
            ],
            "kpi": [
                {
                    "title": "Product A Performance",
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                    "chart": json.dumps(
                        {
                            "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                            "datasets": [{"data": average, "borderColor": "#9333ea"}],
                        }
                    ),
                },
                {
                    "title": "Product B Performance",
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
                {
                    "title": "Product C Performance",
                    "metric": "$1,234.56",
                    "footer": mark_safe(
                        '<strong class="text-green-600 font-medium">+3.14%</strong>&nbsp;progress from last week'
                    ),
                },
            ],
            "progress": [
                {
                    "title": "Social marketing e-book",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Freelancing tasks",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Development coaching",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Product consulting",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
                {
                    "title": "Other income",
                    "description": " $1,234.56",
                    "value": random.randint(10, 90),
                },
            ],
            "chart": json.dumps(
                {
                    "labels": [WEEKDAYS[day % 7] for day in range(1, 28)],
                    "datasets": [
                        {
                            "label": "Example 1",
                            "type": "line",
                            "data": average,
                            "backgroundColor": "#f0abfc",
                            "borderColor": "#f0abfc",
                        },
                        {
                            "label": "Example 2",
                            "data": positive,
                            "backgroundColor": "#9333ea",
                        },
                        {
                            "label": "Example 3",
                            "data": negative,
                            "backgroundColor": "#f43f5e",
                        },
                    ],
                }
            ),
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
        },
    )

    return context
