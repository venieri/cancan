from django.urls import path

from . import views

urlpatterns = [
    path('', views.JHPoker.as_view(), name='videopoker'),
]