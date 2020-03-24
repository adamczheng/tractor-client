class Pair(object):

    def __init__(self, cur_round, card):
        self.card = card
        self.suit = cur_round.get_suit(card)
        self.round = cur_round
        self.card_value = cur_round.card_value(card)

    def __gt__(self, other):
        if self.suit == 'trump' and other.suit != 'trump':
            return True
        if self.suit == other.suit and self.card_value > other.card_value:
            return True
        return False

    def __eq__(self, other):
        return self.card_value == other.card_value

    def __cmp__(self, other):
        if self.card_value > other.card_value:
            return 1
        elif self.card_value == other.card_value:
            return 0
        else:
            return -1

    def __str__(self):
        return str(self.card)

    def get_card(self):
        return self.card

    def get_suit(self):
        return self.suit

    def __str__(self):
        return 'pair ' + str(self.card)


def contains_pair(self, hand):
    suit = self.get_suit(hand[0])
    return self.contains_pair_in_suit(hand, suit)


# RETURNS THE NUMBER OF PAIRS IN A CERTAIN SUIT
def contains_pair_in_suit(self, hand, suit):
    num_pairs = 0
    for card in hand:
        if self.get_suit(card) != suit:
            continue
        for card2 in hand:
            if card is not card2 and card == card2:
                num_pairs += 1
    num_pairs /= 2
    return num_pairs

