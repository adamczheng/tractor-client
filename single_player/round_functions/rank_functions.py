def compare_value(self, card):
    """
    KNOWN AS self.CARD_VALUE(CARD)
    Returns a relative value of the card.
    Lowest card in a suit is 1, second lowest is 2, etc... highest (usually A) is 12 because one rank is trump
    All cards of trump suit and not in the top 12 will have 100 added to signify trump
    ex: trump_rank == 4, trump_suit == spades
    2d: 1 3d: 2 5d: 3 ... 10d: 8 Jd: 9 Qd: 10 Kd: 11 Ad: 12
    2s: 101 3s: 102 5s: 103 10s: 108 Js: 109 Qs: 110 Ks: 111 As: 112 4d: 113 4c: 113 4s: 114 SJo: 115 BJo: 116

    ex: trump_rank == 4, trump_suit == "none" (wuzhu)
    2d: 1 3d: 2 5d: 3 ... Ad: 12
    4c: 114 4d: 114 4h: 114 4s: 114 SJo: 115 BJo: 116
    :param self: the Round instance
    :param card: found in deck.py file
    :return: int
    """
    trump_rank = self.trump_rank
    trump_suit = self.trump_suit
    if card.is_big_joker:
        return 116
    elif card.is_small_joker:
        return 115
    card_suit = card.get_suit()
    card_rank = card.get_rank()
    if card_rank == trump_rank:
        if card_suit == trump_suit or trump_suit == "none":
            return 114
        else:
            return 113
    rank_dict = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8, '10': 9, 'J': 10, 'Q': 11,
                 'K': 12, 'A': 13}
    temp_card_value = rank_dict[card_rank]
    if temp_card_value > rank_dict[trump_rank]:
        temp_card_value -= 1
    if self.is_trump(card):
        temp_card_value += 100
    return temp_card_value


def view_value(self, card):
    """
    Returns an integer representing the ordering of how cards are viewed in the GUI. Trumps have the highest ranking
    and within each suit, the higher card has a higher ranking.
    :param self: Round object passed in
    :param card:
    :return: int corresponding to ranking in which cards are displayed on GUI
    """
    card_value = self.card_value(card)
    suit_order = {
        'diamonds': 0,
        'clubs': 1,
        'hearts': 2,
        'spades': 3
    }
    r_suit_order = {
        0: 'diamonds',
        1: 'clubs',
        2: 'hearts',
        3: 'spades'
    }

    if self.get_suit(card) == 'trump':
        """Originally, Big Joker is 116, SJo 115, Zhu Rank 114, Fu Rank 113, rest doesn't matter \
        We want to change so that we arbitarily assign order to the Ranks 113, 114, 115, 116 (116 being the Zhu)
        Sjo will be 117, BJo will be 118. And we will add 400 onto this.
        """
        if card_value <= 112:
            return 400+card_value
        if card.is_big_joker:
            return 518
        if card.is_small_joker:
            return 517
        if self.trump_suit == 'none' or self.trump_suit == 'spades':
            order = {'spades': 3, 'hearts': 2, 'clubs': 1, 'diamonds': 0}
        if self.trump_suit == 'hearts':
            order = {'hearts': 3, 'clubs':2, 'diamonds': 1, 'spades': 0}
        if self.trump_suit == 'clubs':
            order = {'clubs': 3, 'diamonds': 2, 'spades': 1, 'hearts': 0}
        if self.trump_suit == 'diamonds':
            order = {'diamonds': 3, 'spades': 2, 'hearts': 1, 'clubs': 0}
        return 513 + order[card.get_suit()]



    if self.trump_suit == 'none':
        if self.get_suit(card) == 'spades':
            return 300+card_value
        if self.get_suit(card) == 'hearts':
            return 200+card_value
        if self.get_suit(card) == 'clubs':
            return 100+card_value
        return card_value
    else:
        trump_suit = self.trump_suit
        suit_index = suit_order[trump_suit]
        for i in range(suit_index, suit_index+4):
            c_index = i % 4
            if self.get_suit(card) == r_suit_order[c_index]:
                return 100*(4-(i-suit_index)) + card_value


def cmp_cards(self, a, b):
    """
    Compares cards in the context of the round. Returns 0 if cards are same, 1 if a>b, and -1 if a<b
    :param self: round instance
    :param a: Card 1
    :param b: Card 2
    :return: int (-1, 0, or 1)
    """
    if a == b:
        return 0
    if a.is_big_joker:
        return 1
    if b.is_big_joker:
        return -1
    if a.is_small_joker:
        return 1
    if b.is_small_joker:
        return -1
    if a.rank == self.trump_rank and a.suit == self.trump_suit:
        return 1
    if b.rank == self.trump_rank and b.suit == self.trump_suit:
        return -1
    if a.rank == self.trump_rank and b.rank == self.trump_rank:
        return 0
    if a.rank == self.trump_rank:
        return 1
    if b.rank == self.trump_rank:
        return -1

    suit_dict = {'clubs': 1, 'diamonds': 2, 'hearts': 3, 'spades': 4, self.suit_played: 5, self.trump_suit: 6}
    rank_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                 'K': 13, 'A': 14, self.trump_rank: 15}
    if suit_dict[a.suit] > suit_dict[b.suit]:
        return 1
    elif suit_dict[a.suit] < suit_dict[b.suit]:
        return -1
    else:
        if rank_dict[a.rank] > rank_dict[b.rank]:
            return 1
        else:
            return -1
