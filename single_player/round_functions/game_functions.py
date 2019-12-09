from single_player.deck import *

def play_round(self):
    self.game_start = True
    self.deal()

    # play out the turns
    # pass in trump info as a dictionary
    info = self.play_turn(self.zhuang_jia_id)
    self.clear = True
    while len(self.players[0].get_hand()) > 0:

        # assumes that play_turn return an info dictionary
        trick_winner = info['trick_winner']
        self.current_player = trick_winner
        info = self.play_turn(trick_winner)

    # reveal di pai and add to attacker's points if necessary
    attacker_multiplier = 2 * info['num_cards']
    if (info['trick_winner'] == self.zhuang_jia_id) or (info['trick_winner'] == (self.zhuang_jia_id + 2) % 4):
        attacker_multiplier = 0

    di_pai_points = 0
    print("Di pai: ", end='')
    for card in self.discards:
        di_pai_points += card.point_value
        print(card, end=' ')
    print('')

    if attacker_multiplier > 0:
        print("Attackers won the last trick, adding %d * %d = %d points."
              % (attacker_multiplier, di_pai_points, attacker_multiplier * di_pai_points))
        self.attacker_points += attacker_multiplier * di_pai_points

    return self.attacker_points


def deal(self):
    self.deck.shuffle()
    current_drawer = self.zhuang_jia_id
    while len(self.deck) > self.num_di_pai:
        self.players[current_drawer].draw(self.deck.pop())
        # print(self.players[current_drawer].name)
        # self.players[current_drawer].print_hand()
        while True:
            if self.liang_query(current_drawer) == 'space':
                self.client_input = ''
                break
        for player in self.players:
            player.hand.sort(key=self.view_value, reverse=True)
        current_drawer = (current_drawer + 1) % 4
    # no liang -> flip di pai
    if self.trump_suit == "none":
        self.flip_di_pai()
    for player in self.players:
        player.hand.sort(key=self.view_value,reverse=True)
    # zhuang jia chooses 8 cards for di pai
    self.choose_di_pai()

def liang_query(self, current_drawer):
    # format is "suit cnt" or "SJo 2" or "BJo 2"
    # print("Liang?")
    response = get_player_input(self, current_drawer)
    # space means skip liang
    if response == 'space':
        # print("No liang, continuing")
        return response
    # check for validity of the response
    if is_valid_input(self, self.players[current_drawer], response):
        response = [self.players[current_drawer].get_hand()[i] for i in response]
        if len(response) > 2 or len(response) <= 0:
            # print("invalid response, continuing")
            return
        if len(response) == 1:
            if response[0].get_rank() == self.players[0].get_trump_rank() and self.trump_suit_cnt < 1:
                self.trump_suit = response[0].get_suit()
                self.trump_suit_cnt = 1
                return 'space'
        elif len(response) == 2:
            if response[0] == response[1]:
                if response[0].get_rank() == self.players[0].get_trump_rank() and self.trump_suit_cnt < 2:
                    self.trump_suit = response[0].get_suit()
                    self.trump_suit_cnt = 2
                    return 'space'
                elif response[0].get_is_joker():
                    self.trump_suit = 'wu zhu'
                    self.trump_suit_cnt = 3
                    return 'space'
                else:
                    return
            else:
                return
        else:
            return
    else:
        return

def flip_di_pai(self):
    """
    Flips cards from di pai until the trump rank or joker is hit, and sets the trump suit accordingly
    Otherwise makes the largest card the trump rank
    :param self: round instance
    """
    print("No liang, flipping di pai...")
    largest_rank_suit = "none"
    largest_rank = 1
    rank_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                 'K': 13, 'A': 14}
    for card in self.deck.cards:
        print(card)
        if card.is_big_joker or card.is_small_joker:
            self.trump_suit = "none"
            print("The game is now WuZhu")
            return
        elif card.rank == self.trump_rank:
            self.trump_suit = card.suit
            print("The trump suit is now %s" % card.suit)
            return
        else:
            if rank_dict[card.rank] > largest_rank:
                largest_rank_suit = card.suit
    self.trump_suit = largest_rank_suit
    print("The trump suit is now %s" % self.trump_suit)
    return


def choose_di_pai(self):
    zhuang_jia_player = self.players[self.zhuang_jia_id]
    self.current_player = self.zhuang_jia_id
    for card in self.deck.cards:
        zhuang_jia_player.draw(card)
    zhuang_jia_player.hand.sort(key=self.view_value,reverse=True)
    print(zhuang_jia_player.get_name() + ". Your hand after di pai:")
    zhuang_jia_player.print_hand()
    print("The trump suit is " + self.trump_suit)
    while len(self.discards) != 8:
        # print("Enter 8 indexes you want to discard:")
        discard_indexes = self.get_player_input(self.zhuang_jia_id)
        if not len(discard_indexes) == 8 or not self.is_valid_input(zhuang_jia_player, discard_indexes):
            continue
        else:
            self.current_player = 5
            self.client_input = ''
            break
    # ADDS DISCARDS TO SELF.DISCARDS, DELETES CARDS FROM PLAYER HAND
    for each_index in discard_indexes:
        self.discards.append(zhuang_jia_player.get_hand()[each_index])
    self.di_pai = True
    self.del_indexes(zhuang_jia_player, discard_indexes)

def get_player_input(self, curr_player):
    # just player indexes, check if integers
    self.current_player = curr_player
    response = self.client_input
    if len(response) == 1 and response[0] == 'space':
        return 'space'

    integer_list = [int(s) for s in response if s.isdigit()]
    return integer_list


def is_valid_input(self, player, response):
    if len(set(response)) != len(response):
        return False
    for each_index in response:
        if int(each_index) < 0 or int(each_index) >= len(player.get_hand()):
            return False
    return True


from single_player.round_functions.hand_functions import Hand, SecondaryHand


def play_turn(self, sp_index):
    def get_first_player_move(first_player):
        self.current_player = self.players.index(first_player)
        fp_input = self.get_player_input(self.current_player)

        # Check if input is a list of valid indexes
        if not self.is_valid_input(first_player, fp_input):
            return get_first_player_move(first_player)

        fp_hand = Hand(first_player.get_hand(), self)
        fp_playhand_list = [fp_hand.hand[each_index] for each_index in fp_input]
        fp_playhand = Hand(fp_playhand_list, self, suit=self.get_suit(fp_playhand_list[0]))

        if not fp_playhand.check_is_one_suit(fp_playhand.suit):
            return get_first_player_move(first_player)

        cur_suit = fp_playhand.suit

        # FOR NOW, JUST CHECK IF PAIR OR SINGLE
        '''
        Change to a function of hand in context of round and player's hand eventually
        '''
        if not self.is_valid_fpi(fp_playhand):
            return get_first_player_move(first_player)

        # CHECK FOR LARGEST TRACTOR, LARGEST PAIR, THEN LARGEST SINGLE

        # delete cards once everything is processed
        fp_hand.del_indexes(fp_input)
        return fp_playhand

    def get_secondary_player_move(player, first_hand):
        nonlocal biggest_hand
        nonlocal biggest_player
        self.current_player = self.players.index(player)
        cur_suit = first_hand.suit
        print("Current suit: " + cur_suit + ", current hand size: " + len(first_hand))
        np_input = self.get_player_input(self.current_player)
        if not self.is_valid_input(player, np_input) or not len(first_hand) == len(np_input):
            return get_secondary_player_move(player, first_hand)

        np_hand = Hand(player.get_hand(), self)
        np_playhand_list = [np_hand.hand[each_index] for each_index in np_input]
        np_playhand = SecondaryHand(first_hand, np_playhand_list, self, cur_suit) #Should we pass in suit here?

        np_playhand.check_is_legal_move()
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
                        return {'move_code': 'insufficient number of tractors of length ' + str(tractor_length)}
                    else:
                        break  # Stops checking if they have played a tractor or not if their largest tractor is already played
        has_bigger_hand = np_playhand > biggest_hand
        biggest_hand = np_playhand if has_bigger_hand else biggest_hand
        biggest_player = player if has_bigger_hand else biggest_player
        if hand_size == 1:  # single card
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

        if hand_size > 2:  # TRACTOR ANALYSIS
            if self.contains_tractor_of_length_in_suit(npi_hand, tractor_length,
                                                       cur_suit) or self.contains_tractor_of_length_in_suit(npi_hand,
                                                                                                            tractor_length,
                                                                                                            'trump'):
                our_tractor = self.return_tractors(npi_hand)
                their_tractor = biggest_hand[0]
                has_bigger_tractor = self.tractor_gt(our_tractor, their_tractor)
                return {'move_code': 'valid',
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

    self.cards_played = {0: [], 1: [], 2: [], 3: []}
    first_player = self.players[sp_index]
    print("Hello " + first_player.get_name() + '. Please enter the cards you would like to play.'
                                               ' Attacker current points: ' + str(self.attacker_points))

    first_player.print_hand()

    first_hand = self.get_first_player_move(first_player)

    self.current_player = 5
    self.client_input = ''

    self.cards_played[sp_index] = first_hand
    current_turn_points = 0
    current_turn_points += first_hand.get_num_points()
    '''info_dict = {'suit': fpi['suit'],
                 'hand_type': fpi['hand_type'],
                 'size': fpi['size'],
                 'biggest_hand': fpi['fp_playhand'],
                 'biggest_player': first_player}
    '''
    biggest_hand = first_hand
    biggest_player = first_player

    for i in range(sp_index + 1, sp_index + 4):
        cur_player_index = i % 4
        cur_player = self.players[cur_player_index]
        print("Hello " + cur_player.get_name() + '. Please enter the cards you would like to play.'
                                                 ' Attacker current points: ' + str(self.attacker_points) +
              ' Current turn points: ' + str(current_turn_points))
        cur_player.print_hand()

        npi = self.get_secondary_player_move(cur_player, info_dict)
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


