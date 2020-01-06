'''
Created on Oct 21, 2011

@author: tvassila
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import r
from django.utils.copycompat import deepcopy
from django.utils.datastructures import SortedDict

from accounts.models import Account


class BuyForm(forms.Form):
    VALUES = [10, 20, 50, 100, 500, 1000, 5000]
    amount = forms.TypedChoiceField(coerce=int, choices=zip(VALUES, VALUES))


class SigninForm(AuthenticationForm): pass


class RulesForm(forms.Form):
    pass


class JoinForm(UserCreationForm):
    error_css_class = 'ui-state-error'
    xrequired_css_class = 'ui-state-highlight'
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    # referrer = forms.CharField( required=False,  widget=forms.HiddenInput())
    pay = forms.CharField(required=False, help_text='enter the names you want yours winnings cheque made out to.')
    address = forms.CharField(widget=forms.Textarea, required=False,
                              help_text='enter where you want the check sent to...')

    def save(self, commit=True):
        print
        self.cleaned_data['first_name'], self.cleaned_data['username']
        user = super(JoinForm, self).save()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        Account.objects.create(user=user)
        user.get_profile().pay = self.cleaned_data['pay']
        user.get_profile().address = self.cleaned_data['address']
        if commit:
            user.save()
            user.get_profile().save()
        return user

    def required(self):
        return self.subform(('username', 'password1', 'password2'))

    def optional(self):
        return self.subform(('email', 'first_name', 'last_name', 'address'))

    def subform(self, fieldset=()):
        form = deepcopy(self)
        form.fields = SortedDict([(key, self.fields[key]) for key in fieldset])
        return form


class JoinWizard(FormWizard):
    def done(self, request, form_list):
        if not form_list:
            return HttpResponseRedirect(reverse('bounce'))
        form = form_list[1]
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
        return HttpResponseRedirect(reverse('mainhall'))

    def get_template(self, step):
        if step == 0:
            return 'rules.html'
        return 'join.html'

    @method_decorator(csrf_protect)
    def __callx__(self, request, *args, **kwargs):
        if request.POST and request.POST.get('cancel'):
            return self.done(request, [])
        return super(JoinWizard, self).__call__(request, *args, **kwargs)
