import random
import logging
import pickle

from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView

def build_bid_select_field(max_amount, default = 10):
    bids = list(filter(lambda x: x <= max_amount,  [1,5,10,20,50,100,500,1000,5000]))
    if bids:
        default = min(default, max(bids))
        #print default, bids
    else:
        default = 0
    print(max_amount, default, list(zip(bids, bids)))
    return forms.TypedChoiceField(coerce=int, initial=default, choices = zip(bids, bids))

def build_bid_select_field(max_amount, default = 10):
    bids = list(filter(lambda x: x <= max_amount,  [1,5,10,20,50,100,500,1000,5000]))
    if bids:
        default = min(default, max(bids))
        #print default, bids
    else:
        default = 0
    print('build_bid_select_field', max_amount, default, list(zip(bids, bids)))
    return forms.TypedChoiceField(coerce=int, initial=default, choices = zip(bids, bids))


def get_form_class(request):
    class BidForm(forms.Form):
        bid = build_bid_select_field(request.user.account.bankroll)
    return BidForm

from utils.cards import Deck, Hand, multiples

log = logging.getLogger(__name__)

ODDS=(('no hand', 0),
    ('Low Pair', 0),
    ('Jacks High', 1),
    ('Two Pairs', 2),
    ('3 of a Kind', 3),
    ('Straight', 4),
    ('Flush', 6),
    ('Full House',9),
    ('4 of a Kind',25),
    ('Straight Flush',50),
    ('Royal Flush',250))

START_MESSAGE="Welcome to Jacks High"
DRAW_MESSAGE="Go on draw your next cards"
BUSTED_MESSAGE="Sorry, you're BUSTED!"
WON_MESSAGE="<br>Wow You've won %.0f"
LOST_MESSAGE="Sorry you lost, try another hand?"

def deal():
    deck = Deck()
    deck.suffle()
    hand = Hand()
    for card in range(5):
        hand.take(deck.deal())
    print('deal', [(card.open, card.ordinal) for card in hand])
    return deck, hand



decorators = [never_cache, login_required]

@method_decorator(decorators, name='dispatch')
class JHPoker(TemplateView):
    template_name = "jhpoker.html"

    def post(self, request):
        winnings = 0
        bid = 0
        account = request.user.account
        message = ''
        action = 'DEAL'
        current_state = request.session.get('next_state', 'start')
        form = get_form_class(request)(request.POST)
        print('state', current_state)
        print('form.is_valid()', form.is_valid())
        if form.is_valid():
            if current_state == 'start':
                deck, hand = deal()
                request.session['next_state'] = 'delt'
                message = "Choose your bid and click on deal"
                action = 'DEAL'
            elif current_state == 'delt':
                bid = form.cleaned_data['bid']
                hand = Hand.from_json(request.session['hand'])
                deck = Deck.from_json(request.session['deck'])
                log.debug('delt %s', current_state)
                request.user.account.bid('jackpot', bid)
                for card in range(5):
                    hand[card].show()
                print('delt', [(card.open, card.ordinal) for card in hand])
                request.session['hand'] = hand.to_json()
                request.session['deck'] = deck.to_json()
                request.session['next_state'] = 'drawn'
                message = "Choose which cards to keep  and click on deal"
                action = 'DRAW'
            elif current_state == 'drawn':
                print(request.POST)
                request.session['next_state'] = 'delt'
                bid = form.cleaned_data['bid']
                hand = Hand.from_json(request.session['hand'])
                deck = Deck.from_json(request.session['deck'])
                for card in range(5):
                    if 'holdcard-%d' % card not in request.POST:
                        hand[card] = deck.deal().show()
                        print('holdcard-%d' % card,  'holdcard-%d' % card not in request.POST, hand[card])
                print('drawn', [(card.open, card.ordinal) for card in hand])
                score = scorer(hand)
                handname, odds = ODDS[score]
                winnings = odds * bid
                request.user.account.win('vpoker', winnings, bid)

                message = handname
                if odds:
                    message += WON_MESSAGE % winnings
                elif request.user.account.bankroll > 1:
                    message = LOST_MESSAGE
                else:
                    message = BUSTED_MESSAGE
                deck_1, hand_1 = deal()
                request.session['hand'] = hand_1.to_json()
                request.session['deck'] = deck_1.to_json()
                action = 'DEAL'

        params = dict(
            action=action,
            hand=hand,
            current_state=current_state,
            next_state=request.session['next_state'],
            account=request.user.account,
            message=message,
            bid=bid,
            winnings=winnings,
            form=form)
        return render(request, "jhpoker.html", params)

    def get(self, request):
        winnings = 0
        bid = 0
        message = ''
        action = 'DEAL'
        current_state = 'start'
        log.debug('start %s', current_state)
        form = get_form_class(request)()
        print(form)
        deck, hand = deal()
        request.session['hand'] = hand.to_json()
        request.session['deck'] = deck.to_json()
        message = "Choose your bid and click on deal"
        request.session['next_state'] = 'delt'
        action = 'DEAL'
        params = dict(
                  action = action,
                 hand = request.session['hand'],
                 current_state = current_state,
                 next_state = request.session['next_state'],
                 account = request.user.account,
                 message = message,
                 bid  = bid,
                 winnings = winnings,
                 form = form)

        return render(request, "jhpoker.html", params)


def jhi_Poker_scorer(hand):
    log.debug('scoring %s', hand.show())
    values = [card.value for card in hand]
    suites = [card.suite for card in hand]
    smax = max(suites)
    smin = min(suites)
    size = len(hand)
    flush = 0
    straight = 0
    vmax = max(values)
    vmin = min(values)
    vdiff = vmax - vmin + 1
    score = 0
    # print ' is straight ? %d == %d ' % (vdiff , size)
    if vdiff == size:  # straight
        # print 'straight'
        straight = 1
    elif vmin == 1 and vmax == 13:  # good chance royal straight
        svalues = values
        svalues.sort()
        # print 'svalues', svalues
        svalues[0] = 14
        vmax = max(svalues)
        vdiff = vmax - min(svalues) + 1
        if vdiff == size:
            straight = 1
    if straight:
        score = 5
    # print ' is flush ? %d == %d ' % (smin , smax)
    if smax == smin:  # flush
        flush = 1
        if straight:
            if vmax == 14:
                score = 10
            else:
                score = 9
        else:
            score = 6
    log.debug('hjiPokerScorer-score %s', score)
    mscore = 0
    if score < 9:
        # print 'check for multiples'
        mscore = multiples(hand)
    log.debug('hjiPokerScorer-score %s', mscore)
    if mscore > 0:
        score = mscore
    elif score > 0:
        hand.cards = map(hold, hand)
    return score


def multiples2(hand):
    i = 0
    pairs = {}
    score = 0
    size = len(hand.cards)
    for i in range(size - 1):
        for j in range(i, size):
            if i != j and hand.cards[i].value == hand.cards[j].value:
                hand.cards[i].state = 9
                hand.cards[j].state = 9
                if pairs.has_key(hand.cards[i].value):
                    pairs[hand.cards[i].value] = pairs[hand.cards[i].value] + 1
                else:
                    pairs[hand.cards[i].value] = 1
                    # print pairs
    npairs = len(pairs)
    if npairs:
        series = []
        for p in pairs.keys():
            series.append(p)
        #    return (series, pairs)
        # now jh specific
        ascore = {1: 1, 2: 4, 3: 4, 6: 8}
        a = series[0]
        # print series
        number = pairs[a]
        score = ascore[number]
        if number == 1:
            if a > 10 or a == 1:
                score = 2
        if npairs == 2:
            bscore = {1: 3, 3: 7}
            b = series[1]
            number = pairs[b]
            if number == 1:
                if score == 4:
                    score = 7

                else:
                    score = 3
            elif number == 3:
                score = 7
    return score


def hold(card):
    card.setState(9)
    return card


def scorer(hand):
    log.debug('scoring %s', hand.show())
    values = [card.value for card in hand]
    suites = [card.suite for card in hand]
    smax = max(suites)
    smin = min(suites)
    size = len(hand)
    flush = 0
    straight = 0
    vmax = max(values)
    vmin = min(values)
    vdiff = vmax - vmin + 1
    score = 0
    # print ' is straight ? %d == %d ' % (vdiff , size)
    if vdiff == size:  # straight
        # print 'straight'
        straight = 1
    elif vmin == 1 and vmax == 13:  # good chance royal straight
        svalues = values
        svalues.sort()
        # print 'svalues', svalues
        svalues[0] = 14
        vmax = max(svalues)
        vdiff = vmax - min(svalues) + 1
        if vdiff == size:
            straight = 1
    if straight:
        score = 5
    # print ' is flush ? %d == %d ' % (smin , smax)
    if smax == smin:  # flush
        flush = 1
        if straight:
            if vmax == 14:
                score = 10
            else:
                score = 9
        else:
            score = 6
    log.debug('hjiPokerScorer-score %s', score)
    mscore = 0
    if score < 9:
        # print 'check for multiples'
        mscore = multiples(hand)
    log.debug('hjiPokerScorer-mscore %s', mscore)
    if mscore > 0:
        score = mscore
    elif score > 0:
        hand.cards = map(hold, hand)
    return score


def jhPokerScorer(hand):
    values = hand.values()
    # print values
    suites = hand.suites()
    smax = max(suites)
    smin = min(suites)
    size = len(hand.cards)
    flush = 0
    straight = 0
    vmax = max(values)
    vmin = min(values)
    vdiff = vmax - vmin + 1
    score = 0
    # print ' is straight ? %d == %d ' % (vdiff , size)
    if vdiff == size:  # straight
        # print 'straight'
        straight = 1
    elif vmin == 1 and vmax == 13:  # good chance royal straight
        svalues = values
        svalues.sort()
        # print 'svalues', svalues
        svalues[0] = 14
        vmax = max(svalues)
        vdiff = vmax - min(svalues) + 1
        if vdiff == size:
            straight = 1
    if straight:
        score = 5
    # print ' is flush ? %d == %d ' % (smin , smax)
    if smax == smin:  # flush
        flush = 1
        if straight:
            if vmax == 14:
                score = 10
            else:
                score = 9
        else:
            score = 6

    mscore = 0
    if score < 9:
        # print 'check for multiples'
        mscore = multiples(hand)
    if mscore > 0:
        score = mscore
    elif score > 0:
        hand.cards = map(hold, hand.cards)
    return score


def holdOn(state):
    if state == 9:
        return "CHECKED"
    return ""