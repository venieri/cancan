"""cancan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.Doorway.as_view(), name="doorway"),
    path('membership_agreement/', views.MembershipAgreement.as_view(), name="membership_agreement"),
    path('join/', views.Join.as_view(), name="join"),
    path('sign_in/', views.SignIn.as_view(), name="sign_in"),
    path('mainhall/', views.Mainhall.as_view(), name="mainhall"),
    path('games/', views.Games.as_view(), name="games"),
    path('manager/', views.Manager.as_view(), name="manager"),
    path('private/', views.Mainhall.as_view(), name="private"),
    path('pit/', views.Pit.as_view(), name="pit"),
    path('arcade/', views.Arcade.as_view(), name="arcade"),
    path('exit/', views.Mainhall.as_view(), name="exit"),
    path('baccarra/', views.Mainhall.as_view(), name="baccarra"),
    path('bjack/', views.Mainhall.as_view(), name="bjack"),
    path('craps/', views.Mainhall.as_view(), name="craps"),
    path('videopoker/', include('videopoker.urls')),
    path('jackpot/', include('jackpot.urls')),
    path('roulette/', include('roulette.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
