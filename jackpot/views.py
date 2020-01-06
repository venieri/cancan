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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache



def build_bid_select_field(max_amount, default = 10):
    bids = list(filter(lambda x: x <= max_amount,  [1,5,10,20,50,100,500,1000,5000]))
    if bids:
        default = min(default, max(bids))
        #print default, bids
    else:
        default = 0
    print(max_amount, default, list(zip(bids, bids)))
    return forms.TypedChoiceField(coerce=int, initial=default, choices = zip(bids, bids))


fruit_odds = {
    'eye': [0.0, 0.04, 0],  # 'eye'    :[0.0, 0.02, 0],
    'seven': [0.1, 0.25, 0],  # 'seven':[0.1, 0.25, 0],
    'cherry': [0.25, 0.45, 0],  # [0.25, 0.45, 0],
    'hand': [0.6, 0.75, 0],
    'fish': [0.75, 0.8, 0],
    'grape': [0.8, 0.95, 0],
    'diamond': [0.95, 1.0, 0]}

payout = {
    'eye eye eye': 250,
    'seven seven seven': 30,
    'cherry cherry cherry': 15,
    'hand hand hand': 10,
    'grape grape grape': 10,
    'diamond diamond diamond': 10,
    'cherry cherry ANY': 3}


def get_fruit(fruits):
    fruit = None
    while not fruit:
        randval = random.random()
        for fruit in fruit_odds:
            odds = fruit_odds[fruit]
            if odds[0] <= randval < odds[1]:
                fruit_odds[fruit][2] = fruit_odds[fruit][2] + 1
                break
        else:
            fruit = 'fish'
        if fruit in fruits:
            fruit = None

    return fruit


def get_different_fruit(fruit):
    for key in fruit_odds.keys():
        if key != fruit:
            return key


def spin_wheel():
    midf = get_fruit(())
    topf = get_fruit((midf,))  # if midf != 'fish' else ())
    botf = get_fruit((midf, topf))  # if topf != 'fish' else (midf))
    return dict(top=topf, mid=midf, bottom=botf)


def calc_score(left, middle, right):
    line = "%s %s %s" % (left, middle, right)
    if line in payout:
        return payout[line], line  # 'three %s' % middle
    else:
        score = 0
        if left == 'cherry':
            score += 1
        if middle == 'cherry':
            score += 1
        if right == 'cherry':
            score += 1
        if score == 2:
            return payout['cherry cherry ANY'], line  # 'two cherries'
    return 0, line  # 'nothing'





decorators = [never_cache, login_required]

@method_decorator(decorators, name='dispatch')
class Jackpot(TemplateView):
    template_name = "join.html"

    def post(self, request):
        account = request.user.account
        form = self.get_form_class(request)(request.POST)
        left_wheel = spin_wheel()
        middle_wheel = spin_wheel()
        right_wheel = spin_wheel()
        if form.is_valid():
            bid = form.cleaned_data['bid']
            if account.bankroll >= bid:
                account.bid('jackpot', bid)
                winnings = 0
                score, fruit = calc_score(
                                        left=left_wheel['mid'],
                                        middle=middle_wheel['mid'],
                                        right=right_wheel['mid']
                                        )
                if score > 0.0:
                    winnings = score * bid
                    account.win('jackpot', winnings, bid)
                    message = '%s, You Won $%d!!' % (fruit, winnings)
                    state = 'won'
                else:
                    message = '%s, Too bad, try again' % fruit
                    state = 'lost'
                params = self.get_params(request, self.get_form_class(request)(), bid)
                params['left_wheel'] = left_wheel
                params['middle_wheel'] = middle_wheel
                params['right_wheel'] = right_wheel
                params['winnings'] = winnings
                params['state'] = state
                params['message'] = message
                return render(request, "jackpot.html", params)
        return render(request, "jackpot.html", self.get_params(request, self.get_form_class(request)))

    def get(self, request):
        return render(request, "jackpot.html", self.get_params(request, self.get_form_class(request)()))

    def get_form_class(self, request):
        class BidForm(forms.Form):
            bid = build_bid_select_field(request.user.account.bankroll)
        return BidForm

    def get_params(self, request, form, bid=0):
        return {
            'state': 'nobid',
            'account': request.user.account,
            'message': 'Spin to Win',
            'left_wheel': spin_wheel(),
            'middle_wheel': spin_wheel(),
            'right_wheel': spin_wheel(),
            'bid': 0,
            'winnings': 0,
            'form': form
        }
