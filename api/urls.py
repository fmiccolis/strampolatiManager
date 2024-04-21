from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('events/<str:year>', views.yearDetail, name="year_detail"),
    path('events/<str:year>/<str:month>', views.monthDetail, name="month_detail")
]
