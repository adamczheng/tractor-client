"""
structure for cards
structure for deck
note: trumps ignored
"""
import random


class Card(object):
    """
    rank = string
    suit = string
    is_trump = boolean
    is_big_joker = boolean
    is_small_joker = boolean
    """

    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    suit_map = {'clubs': '\u2663', 'diamonds': '\u2666', 'hearts': '\u2665', 'spades': '\u2660'}

    def __init__(self, rank, suit, ID=0, is_big_joker=False, is_small_joker=False):
        self.rank = rank
        self.suit = suit
        self.ID = ID
        self.is_big_joker = is_big_joker
        self.is_small_joker = is_small_joker
        self.is_joker = is_big_joker or is_small_joker
        if self.rank == '5':
            self.point_value = 5
        elif self.rank == '10' or self.rank == 'K':
            self.point_value = 10
        else:
            self.point_value = 0

    def __str__(self):
        if self.is_big_joker:
            return 'BJo'
        if self.is_small_joker:
            return 'SJo'
        return self.rank + Card.suit_map[self.suit]

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.is_big_joker and other.is_big_joker:
            return True
        if self.is_small_joker and other.is_small_joker:
            return True
        if self.is_joker:
            return False
        if self.rank == other.rank and self.suit == other.suit:
            return True
        return False

    def get_suit(self):
        return str(self.suit)

    def get_rank(self):
        return str(self.rank)

    def get_is_joker(self):
        return True if self.is_joker else False

    def get_is_big_joker(self):
        return True if self.is_big_joker else False

    def get_is_small_joker(self):
        return True if self.is_small_joker else False


class Deck(object):
    def __init__(self):
        self.cards = []
        i = 0
        for r in Card.ranks:
            for s in Card.suits:
                self.cards.append(Card(r, s, i))
                i += 1
                self.cards.append(Card(r, s, i))
                i += 1
        self.cards.append(Card('', '', i, False, True))
        i += 1
        self.cards.append(Card('', '', i, False, True))
        i += 1
        self.cards.append(Card('', '', i, True, False))
        i += 1
        self.cards.append(Card('', '', i, True, False))
        i += 1
        assert (i == 108)

    def shuffle(self):
        random.shuffle(self.cards)

    def shuffle_seed(self, seed_function):
        random.shuffle(self.cards, seed_function)

    def pop(self):
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def print_deck(self):
        for s in self.cards:
            print(s)

    def get_len(self):
        return len(self.cards)

SMALL_JOKER = Card('', '', 0, False, True)
BIG_JOKER = Card('', '', 0, True, False)
# deck = Deck()
# deck.print_deck()
