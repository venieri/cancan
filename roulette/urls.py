from django.urls import path

from . import views

urlpatterns = [
    path('', views.Spin.as_view(), name='roulette'),
]