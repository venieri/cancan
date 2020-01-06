from django.shortcuts import render

# Create your views here.
'''
Created on Oct 27, 2011

@author: tvassila
'''
# Create your views here.
import logging, json, time

logger = logging.getLogger(__name__)

from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django import forms
import random

thousands = lambda x: ((x*4//5)//1000)
fivehundreds = lambda x:((x-thousands(x)*1000)*3//4)//500
hundreds = lambda x:((x-thousands(x)*1000 - fivehundreds(x)*500)*4//5)//100
fifties = lambda x:((x-thousands(x)*1000 - fivehundreds(x)*500 - hundreds(x)*100)*2//3)//50
twenties = lambda x:((x-thousands(x)*1000 - fivehundreds(x)*500 - hundreds(x)*100-fifties(x)*50)*3//4)//20
tens = lambda x:((x-thousands(x)*1000 - fivehundreds(x)*500 - hundreds(x)*100-fifties(x)*50-twenties(x)*20))//10

def bankroll(amount,  dominations=((1000,thousands), (500,fivehundreds), (100, hundreds), (50, fifties), (20, twenties), (10, tens))):
    chips=[]
    amount = int(amount)
    for value,func in dominations:
        f = func
        x = func(amount)
        chips += [value]* x
    return chips

class ChipStack(list):
    def __init__(self, bid, chips):
        super(self, ChipStack).__init__(chips)
        self.bid = bid


START_MESSAGE = "Welcome to The Table"
BUST_MESSAGE = "Sorry, you're BUSTED!"
WON_MESSAGE = "Congratulations,  You've won %.0f"
LOST_MESSAGE = "Place your bets"


def spin_ball():
    return random.choice((0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14,
                          31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26))



from django.views.generic import TemplateView

_bankroll = 100000
class BidForm(forms.Form):
    chips = forms.TextInput()

decorators = [never_cache, login_required]

@method_decorator(decorators, name='dispatch')
class Spin(TemplateView):
    template_name = "roulette.html"

    def get(self, request):
        return render(request, "roulette.html", {'ball': spin_ball(),
                  'chips': [dict(id='chip-%d' % i, value=value, state='start') for i, value in enumerate(bankroll(request.user.account.bankroll))],
                  'form': BidForm(),
                  'payout_js': json.dumps([]),
                  'payout': []}
                       )


    def post(self, request):
        ball = spin_ball()
        form = BidForm(request.POST)
        if form.is_valid() and _bankroll > 0:
            chips = request.POST.get('chips')
            # print chips
            chips = json.loads(chips) if chips else []
            # print 'CHIPS IN', chips
            total_bid, total_won, total_lost, winning_bids, winStack, loosingBids = croupierCollect(ball, chips,
                                                                                                    odds, table)
            # account.bid('roulette', total_bid)
            if total_won:
                message = WON_MESSAGE % total_won
                logger.debug('before wonOnMany')
                # account.win('roulette', total_won + winning_bids, total_bid)
                logger.debug('before won flash')
            elif 10 > 1: #account.bankroll > 1:
                message = LOST_MESSAGE
                logger.debug('before lost flash')
            else:
                message = BUST_MESSAGE
                logger.debug('before lost flash')
            payout = croupierPayout(winStack)
            params = {'payout_js': json.dumps(payout),
                      'payout': payout,
                      'bid': total_bid,
                      'won': total_won,
                      'winningBids': winning_bids,
                      'loosingBids': loosingBids,
                      }
        return render(request, "roulette.html", {'ball': spin_ball(),
                  'chips': [dict(id='chip-%d' % i, value=value, state='start') for i, value in enumerate(bankroll(10000))],
                  'form': BidForm(),
                  'payout_js': json.dumps([]),
                  'payout': []}
                       )

@login_required
@csrf_protect
@never_cache
def spin(request):
    class BidForm(forms.Form):
        chips = forms.TextInput()

    account = request.user.get_profile()
    message = 'Spin to Win'
    ball = spin_ball()
    print
    'BALL', table[ball]
    params = {}
    if request.method == 'GET':
        print
        'spin GET'

        chips = [dict(id='chip-%d' % i, value=value, state='start') for i, value in
                 enumerate(bankroll(account.bankroll))]
    elif request.method == 'POST':
        try:
            print
            'spin POST'
            form = BidForm(request.POST)
            if form.is_valid() and account.bankroll > 0:
                chips = request.POST.get('chips')
                # print chips
                chips = json.loads(chips) if chips else []
                # print 'CHIPS IN', chips
                total_bid, total_won, total_lost, winning_bids, winStack, loosingBids = croupierCollect(ball, chips,
                                                                                                        odds, table)
                account.bid('roulette', total_bid)
                if total_won:
                    message = WON_MESSAGE % total_won
                    logger.debug('before wonOnMany')
                    account.win('roulette', total_won + winning_bids, total_bid)
                    logger.debug('before won flash')
                elif account.bankroll > 1:
                    message = LOST_MESSAGE
                    logger.debug('before lost flash')
                else:
                    message = BUST_MESSAGE
                    logger.debug('before lost flash')
                payout = croupierPayout(winStack)
                print
                'PAYOUT', payout
                params = {'payout_js': json.dumps(payout),
                          'payout': payout,
                          'bid': total_bid,
                          'won': total_won,
                          'winningBids': winning_bids,
                          'loosingBids': loosingBids,
                          }
        except:
            logger.exception("ROULETTE Failed %s" % params)
            print
            "-" * 40
            chips = [dict(id='chip-%d' % i, value=value, state='start') for i, value in
                     enumerate(bankroll(account.bankroll))]
            form = BidForm()
            # print params
            # print message
            # print account.bankroll
            # print 'CHIPS OUT', chips

    values = {'ball': ball,
              'colour_call': table[ball][1][1],
              'ball_call': table[ball][1][0],
              'account': account,
              'message': message,
              'chips': chips,
              'form': form,
              'payout_js': json.dumps([]),
              'payout': []}
    values.update(params)
    # print values
    return render_to_response('roulette.html', values, context_instance=RequestContext(request))


odds = {'Zero': 35,
        '1': 35,
        '2': 35,
        '3': 35,
        '4': 35,
        '5': 35,
        '6': 35,
        '7': 35,
        '8': 35,
        '9': 35,
        '10': 35,
        '11': 35,
        '12': 35,
        '13': 35,
        '14': 35,
        '15': 35,
        '16': 35,
        '17': 35,
        '18': 35,
        '19': 35,
        '20': 35,
        '21': 35,
        '22': 35,
        '23': 35,
        '24': 35,
        '25': 35,
        '26': 35,
        '27': 35,
        '28': 35,
        '29': 35,
        '30': 35,
        '31': 35,
        '32': 35,
        '33': 35,
        '34': 35,
        '35': 35,
        '36': 35,
        '1to3': 11,
        '4to6': 11,
        '7to9': 11,
        '10to12': 11,
        '13to15': 11,
        '16to18': 11,
        '19to21': 11,
        '22to24': 11,
        '25to27': 11,
        '28to30': 11,
        '31to33': 11,
        '34to36': 11,
        '1to34': 2,
        '2to35': 2,
        '3to36': 2,
        '1doz': 2,
        '2doz': 2,
        '3doz': 2,
        'Red': 1,
        'Black': 1,
        'even': 1,
        'odd': 1,
        '1to18': 1,
        '19to36': 1}

tableODDS = 0
tableWINNERS = 1
tableNAME = 0
tableCOLOUR = 1

table = [
    (35.0, ['Zero', 'Green']),
    (35.0, ['1', 'Red', '1to18', 'odd', '1to3', '1to34', '1doz']),
    (35.0, ['2', 'Black', '1to18', 'even', '1to3', '2to35', '1doz']),
    (35.0, ['3', 'Red', '1to18', 'odd', '1to3', '3to36', '1doz']),
    (35.0, ['4', 'Black', '1to18', 'even', '4to6', '1to34', '1doz']),
    (35.0, ['5', 'Red', '1to18', 'odd', '4to6', '2to35', '1doz']),
    (35.0, ['6', 'Black', '1to18', 'even', '4to6', '3to36', '1doz']),
    (35.0, ['7', 'Red', '1to18', 'odd', '7to9', '1to34', '1doz']),
    (35.0, ['8', 'Black', '1to18', 'even', '7to9', '2to35', '1doz']),
    (35.0, ['9', 'Red', '1to18', 'odd', '7to9', '3to36', '1doz']),
    (35.0, ['10', 'Black', '1to18', 'even', '10to12', '1to34', '1doz']),
    (35.0, ['11', 'Black', '1to18', 'odd', '10to12', '2to35', '1doz']),
    (35.0, ['12', 'Red', '1to18', 'even', '10to12', '3to36', '1doz']),
    (35.0, ['13', 'Black', '1to18', 'odd', '13to15', '1to34', '2doz']),
    (35.0, ['14', 'Red', '1to18', 'even', '13to15', '2to35', '2doz']),
    (35.0, ['15', 'Black', '1to18', 'odd', '13to15', '3to36', '2doz']),
    (35.0, ['16', 'Red', '1to18', 'even', '16to18', '1to34', '2doz']),
    (35.0, ['17', 'Black', '1to18', 'odd', '16to18', '2to35', '2doz']),
    (35.0, ['18', 'Red', '1to18', 'even', '16to18', '3to36', '2doz']),
    (35.0, ['19', 'Red', '19to36', 'odd', '19to21', '1to34', '2doz']),
    (35.0, ['20', 'Black', '19to36', 'even', '19to21', '2to35', '2doz']),
    (35.0, ['21', 'Red', '19to36', 'odd', '19to21', '3to36', '2doz']),
    (35.0, ['22', 'Black', '19to36', 'even', '22to24', '1to34', '2doz']),
    (35.0, ['23', 'Red', '19to36', 'odd', '22to24', '2to35', '2doz']),
    (35.0, ['24', 'Black', '19to36', 'even', '22to24', '3to36', '2doz']),
    (35.0, ['25', 'Red', '19to36', 'odd', '25to27', '1to34', '3doz']),
    (35.0, ['26', 'Black', '19to36', 'even', '25to27', '2to35', '3doz']),
    (35.0, ['27', 'Red', '19to36', 'odd', '25to27', '3to36', '3doz']),
    (35.0, ['28', 'Black', '19to36', 'even', '28to30', '1to34', '3doz']),
    (35.0, ['29', 'Black', '19to36', 'odd', '28to30', '2to35', '3doz']),
    (35.0, ['30', 'Red', '19to36', 'even', '28to30', '3to36', '3doz']),
    (35.0, ['31', 'Black', '19to36', 'odd', '31to33', '1to34', '3doz']),
    (35.0, ['32', 'Red', '19to36', 'even', '31to33', '2to35', '3doz']),
    (35.0, ['33', 'Black', '19to36', 'odd', '31to33', '3to36', '3doz']),
    (35.0, ['34', 'Red', '19to36', 'even', '34to36', '1to34', '3doz']),
    (35.0, ['35', 'Black', '19to36', 'odd', '34to36', '2to35', '3doz']),
    (35.0, ['36', 'Red', '19to36', 'even', '34to36', '3to36', '3doz']),
    (11.0, ['1to3', 'Green']),
    (11.0, ['4to6', 'Green']),
    (11.0, ['7to9', 'Green']),
    (11.0, ['10to12', 'Green']),
    (11.0, ['13to15', 'Green']),
    (11.0, ['16to18', 'Green']),
    (11.0, ['19to21', 'Green']),
    (11.0, ['22to24', 'Green']),
    (11.0, ['25to27', 'Green']),
    (11.0, ['28to30', 'Green']),
    (11.0, ['31to33', 'Green']),
    (11.0, ['34to36', 'Green']),
    (2.0, ['1to34', 'Green']),
    (2.0, ['2to35', 'Green']),
    (2.0, ['3to36', 'Green']),
    (2.0, ['1doz', 'Green']),
    (2.0, ['2doz', 'Green']),
    (2.0, ['3doz', 'Green']),
    (1.0, ['Red', 'Red']),
    (1.0, ['Black', 'Black']),
    (1.0, ['even', 'Green']),
    (1.0, ['odd', 'Green']),
    (1.0, ['1to18', 'Green']),
    (1.0, ['19to36', 'Green'])]

import time, random


def croupierCollect(ball, chips, odds, table):
    total_bid = 0
    total_won = 0
    total_lost = 0
    winStack = []
    loosingBids = []
    winning_bids = 0
    for chip in chips:
        bid_split = len(chip['bids'])
        bid_lost = 0
        if bid_split:
            wins = []
            for bid in chip['bids']:
                bid_part = chip['value'] / bid_split
                if bid in table[ball][1]:
                    print
                    bid_split, chip['value']
                    won = bid_part * odds[bid]
                    winning_bids += bid_part
                    wins.append((chip, won, bid_part))
                else:
                    bid_lost += bid_part
            won = sum([value for id, value, _ in wins])
            if wins:
                winStack.append((chip, won - bid_lost, chip['value'] / bid_split))
            else:
                chip['state'] = 'LOST'
            total_won += won
            total_bid += chip['value']
            total_lost += bid_lost
    return total_bid, total_won, total_lost, winning_bids, winStack, loosingBids


def croupierPayout(winningBids):
    newChips = []
    i = 0
    for chip, won, bid_part in winningBids:
        for value in payout(won, chip['value']):
            newChips.append({
                'id': '%d-%d' % (time.time(), i),
                'bids': chip['bids'],
                'state': 'WON',
                'top': int(chip['top']) + i,
                'left': int(chip['left']) + i,
                'value': value
            })
            i += 1
    return newChips




def payout(amount, bid=100):
    chips = []
    amount = int(amount)
    for dom in 1000, 500, 100, 50, 20, 10:
        if dom < amount or dom == bid:
            chips += [dom] * (amount // dom)
            amount -= dom * (amount // dom)
        if amount < 10:
            break
    return chips


