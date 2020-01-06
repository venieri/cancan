import random

from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views.generic import TemplateView

from accounts.models import Account
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse
from copy import deepcopy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView





class JoinForm(UserCreationForm):
    error_css_class = 'is-danger'
    xrequired_css_class = 'ui-state-highlight'
    email = forms.EmailField(required=False)
    agreed_to_rules = forms.BooleanField(required=True)
    wallet = forms.CharField(widget=forms.Textarea, required=False,
                              help_text='enter where you want the check sent to...')

    def save(self, commit=True):
        user = super(JoinForm, self).save()
        account = Account.objects.create(user=user)
        account.agreed_to_rules = self.cleaned_data['agreed_to_rules']
        account.wallet = self.cleaned_data['wallet']
        if commit:
            user.save()
            account.save()
        return user

    def required(self):
        return self.subform(('username', 'password1', 'password2'))

    def optional(self):
        return self.subform(('wallet'))

    def subform(self, fieldset=()):
        form = deepcopy(self)
        form.fields = dict([(key, self.fields[key]) for key in fieldset])
        return form




class Doorway(TemplateView):
    template_name = "doorway.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pot'] =  random.randrange(1000,5000)
        context['top10'] = [account for account in Account.objects.all().order_by('score')]
        return context

class Mainhall(TemplateView):
    template_name = "mainhall.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pot'] =  random.randrange(1000,5000)
        context['top10'] = [account for account in Account.objects.all().order_by('score')]
        return context

class Games(TemplateView):
    template_name = "games.html"

class Pit(TemplateView):
    template_name = "pit.html"

class Arcade(TemplateView):
    template_name = "arcade.html"

class Manager(TemplateView):
    template_name = "manager.html"

class MembershipAgreement(TemplateView):
    template_name = "join.html"

    def get(self, request):
        return render(request, "agreement.html", {})

class Join(TemplateView):
    template_name = "join.html"

    def get(self, request):
        return render(request, "join.html", { 'form': JoinForm()})

    def post(self, request):
        form = JoinForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('mainhall'))
        return render(request, 'join.html', {'form': form})

class SignIn(LoginView):
    template_name = "signin.html"