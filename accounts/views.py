from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse

from . import models

decorators = [never_cache, login_required]
@method_decorator(decorators, name='dispatch')
class Cashier(TemplateView):
    template_name = "cashier.html"


@method_decorator(decorators, name='dispatch')
class Transactions(ListView):
    template_name = "transactions.html"
    model = models.AccountLine
    paginate_by = 10

@method_decorator(decorators, name='dispatch')
class Buy(TemplateView):
    template_name = "buy.html"

    class BuyForm(forms.Form):
        VALUES = [10, 20, 50, 100, 500, 1000, 5000]
        amount = forms.TypedChoiceField(coerce=int, choices=zip(VALUES, VALUES))

    def get(self, request):
        form = self.BuyForm()
        return render(request, "buy.html", {'form':form})

    def post(self, request):
        form = self.BuyForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            request.user.account.buy(amount).save()
            return HttpResponseRedirect(reverse('cashier'))