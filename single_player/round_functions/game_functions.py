from single_player.deck import *

def play_round(self):
    self.game_start = True
    self.deal()

    # play out the turns
    # pass in trump info as a dictionary
    hand_winner = self.play_turn(self.zhuang_jia_id)
    self.clear = True
    while len(self.players[0].get_hand()) > 0:

        # assumes that play_turn return an info dictionary
        self.current_player = hand_winner
        hand_winner = self.play_turn(hand_winner)

    # reveal di pai and add to attacker's points if necessary
    attacker_multiplier = 2 * len(self.cards_played[0])
    if (self.players.index(hand_winner) == self.zhuang_jia_id) or \
            (self.players.index(hand_winner) == (self.zhuang_jia_id + 2) % 4):
        attacker_multiplier = 0

    di_pai_points = 0
    # print("Di pai: ", end='')
    for card in self.discards:
        di_pai_points += card.point_value
        # print(card, end=' ')
    # print('')

    if attacker_multiplier > 0:
        # print("Attackers won the last trick, adding %d * %d = %d points."
        #       % (attacker_multiplier, di_pai_points, attacker_multiplier * di_pai_points))
        self.attacker_points += attacker_multiplier * di_pai_points

    return self.attacker_points


def deal(self, test=False):
    self.deck.shuffle()
    current_drawer = self.zhuang_jia_id
    while len(self.deck) > self.num_di_pai:
        self.players[current_drawer].draw(self.deck.pop())
        # print(self.players[current_drawer].name)
        # self.players[current_drawer].print_hand()
        while not test:
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
    print("Liang?")
    response = get_player_input(self, current_drawer)
    # space means skip liang
    if response == 'space':
        print("No liang, continuing")
        return response
    # check for validity of the response
    if is_valid_input(self, self.players[current_drawer], response):
        response = [self.players[current_drawer].get_hand()[i] for i in response]
        if len(response) > 2 or len(response) <= 0:
            print("invalid response, continuing")
            return
        if len(response) == 1:
            if response[0].get_rank() == self.players[0].get_trump_rank() and self.trump_suit_cnt < 1:
                self.trump_suit = response[0].get_suit()
                self.cards_played[current_drawer].append(response)
                self.trump_suit_cnt = 1
                return 'space'
        elif len(response) == 2:
            if response[0] == response[1]:
                if response[0].get_rank() == self.players[0].get_trump_rank() and self.trump_suit_cnt < 2:
                    self.trump_suit = response[0].get_suit()
                    self.cards_played[current_drawer].append(response)
                    self.trump_suit_cnt = 2
                    return 'space'
                elif response[0].get_is_joker():
                    self.trump_suit = 'wu zhu'
                    self.cards_played[current_drawer].append(response)
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

# TODO: add display of flipped cards
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
        self.cards_played[self.zhuang_jia_id].append(card)
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
    self.cards_played = {0: [], 1: [], 2: [], 3: []}

def get_player_input(self, curr_player):
    # just player indexes, check if integers
    self.current_player = curr_player
    response = self.client_input
    if response == ['space']:
        return 'space'

    integer_list = [int(s) for s in response if s.isdigit()]
    return integer_list


def is_valid_input(self, player, response):
    if len(set(response)) != len(response):
        return False
    if len(response) == 0:
        return False
    for each_index in response:
        if int(each_index) < 0 or int(each_index) >= len(player.get_hand()):
            return False
    return True


from single_player.round_functions.hand_functions import Hand


def play_turn(self, sp_index):

    def get_first_player_move(first_player):
        nonlocal turn_players
        nonlocal turn_hands
        self.current_player = self.players.index(first_player)
        fp_input = self.get_player_input(self.current_player)

        while not self.is_valid_input(first_player, fp_input):
            fp_input = self.get_player_input(self.current_player)
        print(fp_input)

        fp_playhand_list = [first_player.get_hand()[each_index] for each_index in fp_input]
        fp_playhand = Hand(fp_playhand_list, self, suit=self.get_suit(fp_playhand_list[0]))

        if not fp_playhand.check_is_one_suit(fp_playhand.suit):
            return

        '''
        Change to a function of hand in context of round and player's hand eventually
        '''
        # delete cards once everything is processed
        self.del_indexes(first_player, fp_input)
        return fp_playhand

    def get_secondary_player_move(player):
        nonlocal turn_hands
        nonlocal turn_players
        self.current_player = self.players.index(player)
        cur_suit = first_hand.suit
        # print("Current suit: " + cur_suit + ", current hand size: " + len(first_hand))
        np_input = self.get_player_input(self.current_player)
        while not self.is_valid_input(player, np_input) or not len(first_hand) == len(np_input):
            np_input = self.get_player_input(self.current_player)
        print(np_input)

        np_playhand_list = [player.get_hand()[each_index] for each_index in np_input]
        np_playhand = Hand(np_playhand_list, self, first=first_hand)  # Should we pass in suit here?

        np_playhand.check_is_legal_move()
        # Check if it's a legal move
        "To-do: Add points to current_turn_points" \
            "Check if this hand greater than previous biggest hand, update if so"
        self.del_indexes(player, np_input)
        return np_playhand

    def reverse(player_index):
        nonlocal cur_player_index
        nonlocal cur_player
        nonlocal current_turn_points
        print('REVERSI!!')
        current_turn_points -= turn_hands.pop().get_num_points()
        self.cards_played[player_index] = []
        cur_player_index = cur_player_index % 4
        cur_player = self.players[cur_player_index]
        self.set_take_back(False)
        return

    turn_players = [(sp_index + i) % 4 for i in range(4)]
    turn_hands = []
    first_hand = None
    current_turn_points = 0

    first_player = self.players[sp_index]
    '''
    print("Hello " + first_player.get_name() + '. Please enter the cards you would like to play.'
                                               ' Attacker current points: ' + str(self.attacker_points))

    first_player.print_hand()
    '''

    first_hand = get_first_player_move(first_player)

    while not first_hand:
        first_hand = get_first_player_move(first_player)
    turn_hands.append(first_hand)

    self.cards_played = {0: [], 1: [], 2: [], 3: []}

    self.current_player = 5
    self.client_input = ''

    self.cards_played[sp_index] = first_hand.hand

    current_turn_points += first_hand.get_num_points()

    cur_player_index = sp_index + 1
    while len(turn_hands) < 4:
        cur_player_index = cur_player_index % 4
        cur_player = self.players[cur_player_index]
        '''
        print("Hello " + cur_player.get_name() + '. Please enter the cards you would like to play.'
                                                 ' Attacker current points: ' + str(self.attacker_points) +
              ' Current turn points: ' + str(current_turn_points))
        cur_player.print_hand()
        '''

        np_hand = get_secondary_player_move(cur_player)
        while not np_hand:
            if self.take_back:
                return reverse(self.current_player - 1)
            np_hand = get_secondary_player_move(cur_player)
        turn_hands.append(np_hand)

        self.cards_played[cur_player_index] = np_hand.hand
        self.current_player = 5
        self.client_input = ''
        current_turn_points += np_hand.get_num_points()
        cur_player_index += 1

    biggest_index = sp_index
    for i in range(4):
        if turn_hands[i] > turn_hands[biggest_index]:
            biggest_index = i
    biggest_player = turn_players[biggest_index]

    if self.is_attacker(self.players[biggest_player]):
        self.attacker_points += current_turn_points

    return biggest_player


