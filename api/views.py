from django.shortcuts import render
import logging

# Create your views here.

logger = logging.getLogger("custom")


def yearDetail(request, year):
    logger.info(year)
    return render(request, 'admin/year_detail.html', {})


def monthDetail(request, year, month):
    logger.info(year, month)
    return render(request, 'admin/month_detail.html', {})
