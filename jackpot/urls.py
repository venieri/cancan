from django.urls import path

from . import views

urlpatterns = [
    path('', views.Jackpot.as_view(), name='jackpot'),
]