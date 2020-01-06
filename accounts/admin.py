from django.contrib import admin

import logging

logger = logging.getLogger(__name__)

from django.contrib import admin, messages
from . import models

class AccountLineInline(admin.TabularInline):
    model = models.AccountLine
    extra = 0
    list_filter = ['status']
    search_fields = ['entry_type', 'amount']
    date_hierarchy = 'timestamp'
    list_display = [
    'account',
    'timestamp',
    'entry_type',
    'amount',
    'bankroll'
    ]




class AccountAdmin(admin.ModelAdmin):
    list_display =[
        'user',
        'bankroll',
        'bids',
        'won']
    # list_filter = ['status']
    search_fields = ['status', 'user']
    inlines = (AccountLineInline,)


admin.site.register(models.Account, AccountAdmin)
