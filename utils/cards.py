import logging

log = logging.getLogger(__name__)

from random import shuffle, randint


class Card:
    def __init__(self, ordinal=0, value=0, suite=0, open=0):
        self.ordinal = ordinal
        self.value = value
        self.suite = suite
        self.open = open and 1 or 0

    def hide(self):
        self.open = 0
        return self

    def show(self):
        self.open = 1
        return self

    def score(self, scorer):
        return scorer(self.value, self.ordinal)

    def __str__(self):
        return "%d" % (self.open and self.ordinal or 0)

    def to_json(self):
        return vars(self)

    @classmethod
    def from_json(cls, json):
        return cls(**json)




class CardList(object):
    def __init__(self, *cards):
        self.cards = list(cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __setitem__(self, index, card):
        self.cards[index] = card
        return self

    def __repr__(self):
        return self.cards.__repr__()

    def __len__(self):
        return len(self.cards)

    def to_json(self):
        return [card.to_json() for card in self.cards]

    @classmethod
    def from_json(cls, json):
        obj = cls()
        obj.cards = [Card.from_json(card) for card in json]
        return obj

    def debug(self):
        return str(
            [("%d %s" % (card.value, {0: 'b', 1: 'd', 2: 'c', 3: 'h', 4: 's'}[card.suite])) for card in self.cards])


class Deck(CardList):
    CARDvalues = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    CARDsuites = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                  3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
                  4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

    def __init__(self, size=52):
        super(Deck, self).__init__()
        self.cards.extend([Card(card, self.CARDvalues[card], self.CARDsuites[card]) for card in range(1, 53)])

    def suffle(self):
        shuffle(self.cards)
        return self

    def cut_deck(self, position=0):
        if not position:
            position = randint(1, len(self.cards) + 1)
        self.cards = self.cards[position:] + self.cards[:position]
        return self

    def deal(self):
        card = self.cards[0]
        self.cards = self.cards[1:]
        return card




class Shoe(Deck):
    def __init__(self, deck=None, cut=None, multiple=1):
        super(Shoe, self).__init__()
        if not deck:
            deck = Deck()
        self.cards.extend(deck.cards * multiple)
        self.cut = cut if cut else len(self)


class Hand(CardList):
    def take(self, card):
        self.cards.append(card)
        return self

    def show(self):
        return str([("%d %s" % (card.value, {0: 'b', 1: 'd', 2: 'c', 3: 'h', 4: 's'}[card.suite])) for card in self])


def multiples(hand):
    i = 0
    pairs = {}
    score = 0
    size = len(hand)
    for i in range(size - 1):
        for j in range(i, size):
            if i != j and hand[i].value == hand[j].value:
                hand[i].state = 9
                hand[j].state = 9
                if hand[i].value in pairs:
                    pairs[hand[i].value] = pairs[hand[i].value] + 1
                else:
                    pairs[hand[i].value] = 1
    log.debug('multiples-pairs %s', pairs)
    npairs = len(pairs)
    if npairs:
        series = []
        for p in pairs.keys():
            series.append(p)
        #    return (series, pairs)
        # now jh specific
        ascore = {1: 1, 2: 4, 3: 4, 6: 8}
        a = series[0]
        log.debug('multiples-series %s', series)
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
    log.debug('multiples-score %s', score)
    return score


def hold(card):
    card.state = 9
    return card


