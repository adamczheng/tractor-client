"""
Keep track of:
everyone's cards
current Zhuang Jia
Zhuang Jia discard
current trump
current attacker's points

also play the round:
dealing, compare cards, and playing
"""
from typing import Dict, Any

from single_player.deck import *
from single_player.round_functions import outdated_functions, rank_functions, pair_functions
from single_player.round_functions import game_functions_stack as game_functions
from single_player.round_functions.pair_functions import Pair
from single_player.round_functions.tractor_functions import Tractor


connections = []

class Round(object):
    """
    players = list of Player (size = 4) (list of Player object)
    zhuang_jia_id = ID of zhuang jia in players (int)
    set_zhuang_jia = True if there is a zhuang jia at the start of the round (boolean)
    trump_suit = trump suit (string)
    trump_suit_cnt = number of cards used to liang the trump suit (exceptions: 0 if no liang and 3 if wu zhu)
    trump_rank = rank of trump card
    suit_played = suit of first card played (the suit that everyone must follow)
    discards = list of discarded cards by zhuang jia
    attacker_points = # points attackers collected
    """
    num_di_pai = 8
    global connections

    def __init__(self, players):
        self.deck = Deck()
        assert (len(players) == 4)
        self.players = players

        # find ID of zhuang jia, set_zhuang_jia is True if someone is zhuang jia
        self.set_zhuang_jia = False
        for i in range(len(players)):
            if players[i].is_zhuang_jia:
                self.zhuang_jia_id = i
                self.set_zhuang_jia = True

        self.trump_suit = "none"
        self.trump_suit_cnt = 0
        self.trump_rank = players[self.zhuang_jia_id].get_trump_rank()  # assumes there is a zhuang jia
        self.suit_played = "none"
        self.discards = []
        self.attacker_points = 0
        self.current_player = 5
        self.cards_played = {0: [], 1: [], 2: [], 3: []}
        self.hand_stack = []
        self.clear = False
        self.di_pai = False
        self.game_start = False
        self.turn_points = 0
        self.round_over = False
        self.client_input = ''
        self.take_back = False
        # assumes there is a zhuang jia
        print("Round starting: " + players[self.zhuang_jia_id].get_name()
              + " is zhuang jia and the trump rank is " + self.trump_rank)

    def get_players(self):
        return self.players

    def get_deck(self):
        return self.deck

    def get_last_player(self):
        if len(self.hand_stack) > 0:
            return self.hand_stack[-1][0]
        return 5

    def get_first_player_move(self, first_player):
        return game_functions.get_first_player_move(self, first_player)

    def get_secondary_player_move(self, player, first_hand):
        return game_functions.get_secondary_player_move(self, player, first_hand)

    def reverse(self):
        return game_functions.reverse(self)

    def play_round(self):
        """
        This function starts the round (deals cards, etc.) and plays until the end.
        :return: int equal to number of points attacker scored for the round
        """
        return game_functions.play_round(self)

    def play_turn(self, sp_index):
        """
        This function plays a turn.
        :param sp_index:
        :return: index of the player who played the biggest hand
        """
        return game_functions.play_turn(self, sp_index)

    def deal(self):
        """
        This non-pure function shuffles the deck, deals cards, flips di pai if necessary, and then executes the
        choose_di_pai function
        :return: No return value
        """
        return game_functions.deal(self)

    def liang_query(self, current_drawer):
        #Outdated function
        "This function was used for testing while prototyping with a text-based version of the game"
        return game_functions.liang_query(self, current_drawer)

    def card_value(self, card):
        """
        Returns a relative value of the card.
        See single_player.round_functions.rank_functions.compare_value for more detail
        :param card: found in deck.py file
        :return: int
        """
        return rank_functions.compare_value(self, card)

    def view_value(self, card):
        '''
        Returns an integer representing the ordering of how cards are viewed in the GUI. Trumps have the highest ranking
        and within each suit, the higher card has a higher ranking.
        :param card:
        :return:
        '''

        return rank_functions.view_value(self, card)

    def cmp_cards(self, a, b):
        """
        Compares cards in the context of the round. Returns 0 if cards are same, 1 if a>b, and -1 if a<b
        :param a: Card 1
        :param b: Card 2
        :return: int (-1, 0, or 1)
        """
        return rank_functions.cmp_cards(self, a, b)

    def flip_di_pai(self):
        """
        Flips cards from di pai until the trump rank or joker is hit, and sets the trump suit accordingly
        Otherwise makes the largest card the trump rank
        """
        return game_functions.flip_di_pai(self)

    def choose_di_pai(self):
        """
        Function that let's Zhuang Jia discard 8 cards into his di pai
        :return: None
        """
        return game_functions.choose_di_pai(self)

    def get_trump_info(self):
        trump_info = {
            'suit': str(self.trump_suit),
            'rank': str(self.trump_rank)
        }
        return trump_info

    def is_trump(self, card):
        trump_info = self.get_trump_info()
        if card.get_is_joker():
            return True
        if card.get_suit() == trump_info['suit']:
            return True
        if card.get_rank() == trump_info['rank']:
            return True
        return False

    def get_suit(self, card):
        if self.is_trump(card):
            return "trump"
        else:
            return card.get_suit()

    # returns true if pair1 played greater than pair2
    def pair_gt(self, pair1, pair2):
        if pair1.get_suit() == 'trump' and pair2.get_suit() != 'trump':
            return True
        elif pair2.suit == pair2.get_suit():
            if self.cmp_cards(pair1.get_card(), pair2.get_card()) == 1:
                return True
        else:
            return False

    # FINDS A PAIR ON PRECONDITION THAT ENTIRE HAND IS OF ONE SUIT
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

    def contains_tractor_of_length(self, hand, length_tractor):
        """
        This checks if the first player's move is a valid tractor.
        we find the value of each card in the play and add it to a list
        This list is then sorted
        If it is a tractor, it should look something similar to
        (1) [3, 3, 4, 4, 5, 5] etc.
        Since it is already the same suit, we just need to check that we have this type of sequence
        :param hand: the list of cards first player wants to play
        :param length_tractor: the number of pairs in the tractor (min: 2)
        :return:
        """
        assert length_tractor >= 2, 'contains_tractor_of_length function invalid variable'
        assert len(hand) % 2 == 0, 'hand contains odd number of cards in contains_tractor_of_length'
        assert len(hand) == 2 * length_tractor
        card_value_list = []
        for card in hand:
            card_value_list.append(self.card_value(card))
        card_value_list.sort()

        assert len(hand) == len(card_value_list), 'contains_tractor_of_length error'
        for i in range(len(card_value_list)):
            if card_value_list[i] - card_value_list[0] != i % 2:
                return False
        #At this point, should satisfy the format (1) in the documentation
        return True

    def is_valid_fpi(self, hand):
        if len(hand) > 2 and len(hand) % 2 == 0:
            if self.contains_tractor_of_length(hand, len(hand) // 2):
                return True
        if len(hand) == 2:
            if self.contains_pair(hand) == 1:
                return True
        elif len(hand) == 1:
            return True
        else:
            return False

    # ASSUMES ALL CARDS ARE IN SAME SuIT
    def return_tractors(self, hand):
        '''
        Should be a tractor at this point, just need to return in tractor format
        :param hand:
        :return:
        '''
        maxval = 0
        for card in hand:
            maxval = max(self.card_value(card), maxval)
        len_tractor = len(hand) // 2
        return Tractor(maxval, len_tractor)

    def return_pairs(self, hand):
        list_pair = []
        for card in hand:
            for card2 in hand:
                if card is not card2 and card == card2:
                    list_pair.append(Pair(card, self.get_suit(card)))
        return list_pair

    def return_singles(self, hand):
        list_singles = []
        for card in hand:
            list_singles.append(card)
        return list_singles

    def get_num_points(self, hand):
        total = 0
        for card in hand:
            if card.get_rank() == '5':
                total += 5
            elif card.get_rank() == '10' or card.get_rank() == 'K':
                total += 10
        return total

    def num_cards_in_suit(self, hand, suit):
        total = 0
        for card in hand:
            if self.get_suit(card) == suit:
                total += 1
        return total

    def num_pairs_in_suit(self, hand, suit):
        total_pair = 0
        for card in hand:
            if self.get_suit(card) != suit:
                continue
            else:
                for card2 in hand:
                    if card == card2 and card is not card2:
                        total_pair += 1
        total_pair /= 2
        return total_pair

    def contains_tractor_of_length_in_suit(self, hand, length, suit):
        card_value_list = []
        for card in hand:
            if self.get_suit(card) == suit:
                card_value_list.append(self.card_value(card))
        card_value_list.sort()
        if len(card_value_list) < 2 * length:
            return False
        found_tractor = False
        for starting_index in range(len(card_value_list) - 2 * length + 1):
            not_a_tractor = False
            for i in range(starting_index, starting_index + 2 * length):
                if not_a_tractor:
                    break
                if card_value_list[i] - card_value_list[starting_index] != i % 2 - starting_index:
                    not_a_tractor = True

            if not not_a_tractor:
                found_tractor = True
                return True

        return found_tractor

    def tractor_gt(self, tractor1, tractor2):
        if tractor1.get_highest_value() > tractor2.get_highest_value():
            return True
        else:
            return False

    def is_attacker(self, player):
        if player is self.players[self.zhuang_jia_id] or player is self.players[(self.zhuang_jia_id + 2) % 4]:
            return False
        return True

    def del_indexes(self, player, index_response):
        for index in sorted(index_response, reverse=True):
            del player.get_hand()[index]

    def get_player_input(self, curr_player):
        return game_functions.get_player_input(self, curr_player)

    def is_valid_input(self, player, response):
        return game_functions.is_valid_input(self, player, response)

    def get_current_player(self):
        return self.current_player

    def get_data(self):
        data = ''
        data += str(0) + ':' + str(self.players[0].get_hand()) + ':' + str(self.cards_played[0])
        for i in range(3):
            data += ':' + str(i+1) + ':' + str(self.players[i+1].get_hand()) + ':' + str(self.cards_played[i+1])
        data += ':' + str(self.clear) + ':' + str(self.di_pai) + ':' + str(self.game_start) \
                + ':' + str(self.attacker_points) + ':' + str(self.trump_suit) + ':' + str(self.current_player)
        return data

    def set_client_input(self, input):
        self.client_input = input

    def set_take_back(self, input):
        if len(self.hand_stack) != 0:
            self.take_back = input
        else:
            self.take_back = False

    def get_attacker_points(self):
        return self.attacker_points