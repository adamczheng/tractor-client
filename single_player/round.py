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
from single_player.round_functions import game_functions, outdated_functions, rank_functions, pair_functions
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
        self.clear = False
        self.di_pai = False
        self.game_start = False
        self.client_input = ''
        # assumes there is a zhuang jia
        print("Round starting: " + players[self.zhuang_jia_id].get_name()
              + " is zhuang jia and the trump rank is " + self.trump_rank)

    def get_players(self):
        return self.players

    def get_deck(self):
        return self.deck

    def play_round(self):
        """
        This function starts the round (deals cards, etc.) and plays until the end.
        :return: int equal to number of points attacker scored for the round
        """
        return game_functions.play_round(self)

    def deal(self):
        """
        This non-pure function shuffles the deck, deals cards, flips di pai if necessary, and then executes the
        choose_di_pai function
        :return: No return value
        """
        return game_functions.deal(self, True)

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

    def get_first_player_move(self, first_player):
        self.current_player = self.players.index(first_player)
        fp_input = self.get_player_input(self.current_player)

        # Check if input is a list of valid indexes
        if not self.is_valid_input(first_player, fp_input):
            return {"move_code": "invalid indexes"}
        fp_hand = first_player.get_hand()

        # CHECK IF SELECtiON IS ONE SUIT
        suit_list = []
        for each_index in fp_input:
            suit_list.append(self.get_suit(first_player.get_hand()[each_index]))
        suit_set = set(suit_list)
        if len(suit_set) != 1:
            return {"move_code": "suit_set error"}

        else:
            cur_suit = self.get_suit(first_player.get_hand()[fp_input[0]])
        fpi_hand = []
        hand_type = []
        for index in fp_input:
            fpi_hand.append(fp_hand[index])

        # FOR NOW, JUST CHECK IF PAIR OR SINGLE
        if not self.is_valid_fpi(fpi_hand):
            return {"move_code": "invalid move"}

        # CHECK FOR LARGEST TRACTOR, LARGEST PAIR, THEN LARGEST SINGLE
        if len(fpi_hand) > 2: #Should be a valid tractor at this point
            fpi_response = [self.return_tractors(fpi_hand)]
            hand_type.append("tractor" + str(len(fpi_hand) // 2))
        if len(fpi_hand) == 2:
            fpi_response = self.return_pairs(fpi_hand)
            hand_type.append('pair')
        elif len(fpi_hand) == 1:
            fpi_response = self.return_singles(fpi_hand)
            hand_type.append('single')
        return {"move_code": "valid",
                "index_response": fp_input,
                "suit": cur_suit,
                "fpi_hand": fpi_response,
                "hand_type": hand_type,
                "size": len(fpi_hand),
                'points': self.get_num_points(fpi_hand)}



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

    def get_secondary_player_move(self, player, cur_hand_info):
        self.current_player = self.players.index(player)
        cur_suit = cur_hand_info['suit']
        hand_size = cur_hand_info['size']
        print("Current suit: " + cur_suit + ", current hand size: " + str(hand_size))
        np_input = self.get_player_input(self.current_player)
        if not self.is_valid_input(player, np_input):
            return {"move_code": "invalid indexes"}
        if not hand_size == len(np_input):
            return {"move_code": "wrong number of cards"}
        np_hand = player.get_hand()
        npi_hand = []
        for index in np_input:
            npi_hand.append(np_hand[index])

        # CHECK IF PLAYED PROPER NUMBER OF SINGLES AND PAIR IN SAME SUIT
        min_singles = min(self.num_cards_in_suit(np_hand, cur_suit), hand_size)
        if not self.num_cards_in_suit(npi_hand, cur_suit) == min_singles:
            return {'move_code': 'insufficient number of current suit'}
        if min_singles == 2:
            min_pair = min(self.num_pairs_in_suit(np_hand, cur_suit), 1)
            if not self.num_pairs_in_suit(npi_hand, cur_suit) == min_pair:
                return {'move_code': 'insufficient number of pairs'}
        if min_singles > 2:
            tractor_length = hand_size // 2
            min_pair = min(tractor_length, self.num_pairs_in_suit(np_hand, cur_suit))
            if not self.num_pairs_in_suit(npi_hand, cur_suit) == min_pair:
                return {'move_code': 'insufficient number of pairs'}
            for i in range(tractor_length, 1, -1):
                if self.contains_tractor_of_length_in_suit(np_hand, tractor_length, cur_suit):
                    if not self.contains_tractor_of_length_in_suit(npi_hand, tractor_length, cur_suit):
                        return{'move_code': 'insufficient number of tractors of length ' + str(tractor_length)}
                    else:
                        break #Stops checking if they have played a tractor or not if their largest tractor is already played


        biggest_hand = cur_hand_info['biggest_hand']
        biggest_player = cur_hand_info['biggest_player']
        if hand_size == 1: #single card
            npi_response = self.return_singles(npi_hand)
            has_bigger_single = self.cmp_cards(npi_response[0], biggest_hand[0]) > 0
            return {'move_code': 'valid',
                    'index_response': np_input,
                    'npi_hand': npi_response,
                    'biggest_hand': npi_response if has_bigger_single else biggest_hand,
                    'biggest_player': player if has_bigger_single else biggest_player,
                    'points': self.get_num_points(npi_hand)}

        if hand_size == 2 and self.contains_pair(npi_hand):
            npi_response = self.return_pairs(npi_hand)
            has_bigger_pair = self.pair_gt(npi_response[0], biggest_hand[0])
            return {'move_code': 'valid',
                    'index_response': np_input,
                    'npi_hand': npi_response,
                    'biggest_hand': npi_response if has_bigger_pair else biggest_hand,
                    'biggest_player': player if has_bigger_pair else biggest_player,
                    'points': self.get_num_points(npi_hand)}

        if hand_size > 2: #TRACTOR ANALYSIS
            if self.contains_tractor_of_length_in_suit(npi_hand, tractor_length, cur_suit) or self.contains_tractor_of_length_in_suit(npi_hand, tractor_length, 'trump'):
                our_tractor = self.return_tractors(npi_hand)
                their_tractor = biggest_hand[0]
                has_bigger_tractor = self.tractor_gt(our_tractor, their_tractor)
                return{'move_code': 'valid',
                        'index_response': np_input,
                        'npi_hand': [our_tractor] if has_bigger_tractor else biggest_hand,
                        'biggest_hand': player if has_bigger_tractor else biggest_player,
                       'points': self.get_num_points(npi_hand)}

        npi_response = self.return_singles(npi_hand)
        return {'move_code': 'valid',
                'index_response': np_input,
                'npi_hand': npi_response,
                'biggest_hand': biggest_hand,
                'biggest_player': biggest_player,
                'points': self.get_num_points(npi_hand)}

    def is_attacker(self, player):
        if player is self.players[self.zhuang_jia_id] or player is self.players[(self.zhuang_jia_id + 2) % 4]:
            return False
        return True

    def del_indexes(self, player, index_response):
        for index in sorted(index_response, reverse=True):
            del player.get_hand()[index]

    def play_turn(self, sp_index):
        self.cards_played = {0: [], 1: [], 2: [], 3: []}
        first_player = self.players[sp_index]
        print("Hello " + first_player.get_name() + '. Please enter the cards you would like to play.'
                                                   ' Attacker current points: ' + str(self.attacker_points))

        first_player.print_hand()
        while True:
            fpi = self.get_first_player_move(first_player)
            if fpi['move_code'] != 'valid':
                print("ERROR: " + fpi['move_code'])
                continue
            else:
                break
        self.current_player = 5
        self.client_input = ''
        for index in fpi['index_response']:
            self.cards_played[sp_index].append(first_player.get_hand()[index])
        current_turn_points = 0
        current_turn_points += fpi['points']
        info_dict = {'suit': fpi['suit'],
                     'hand_type': fpi['hand_type'],
                     'size': fpi['size'],
                     'biggest_hand': fpi['fpi_hand'],
                     'biggest_player': first_player}
        self.del_indexes(first_player, fpi['index_response'])

        for i in range(sp_index + 1, sp_index + 4):
            cur_player_index = i % 4
            cur_player = self.players[cur_player_index]
            print("Hello " + cur_player.get_name() + '. Please enter the cards you would like to play.'
                                                     ' Attacker current points: ' + str(self.attacker_points) +
                  ' Current turn points: ' + str(current_turn_points))
            cur_player.print_hand()
            while True:
                npi = self.get_secondary_player_move(cur_player, info_dict)
                if npi['move_code'] != 'valid':
                    print("ERROR: " + npi['move_code'])
                    continue
                else:
                    break
            self.current_player = 5
            self.client_input = ''
            for index in npi['index_response']:
                self.cards_played[cur_player_index].append(cur_player.get_hand()[index])
            info_dict['biggest_hand'] = npi['biggest_hand']
            info_dict['biggest_player'] = npi['biggest_player']
            current_turn_points += npi['points']
            self.del_indexes(self.players[cur_player_index], npi['index_response'])

        if self.is_attacker(info_dict['biggest_player']):
            self.attacker_points += current_turn_points

        print(info_dict['biggest_player'].get_name() + ' won the hand with ' + str(npi['biggest_hand'][0]))

        return {'trick_winner': self.players.index(info_dict['biggest_player']),
                'num_cards': info_dict['size']}

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

    def get_attacker_points(self):
        return self.attacker_points