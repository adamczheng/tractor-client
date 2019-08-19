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
from single_player.deck import *
import single_player.player_input_methods as pim


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
        self.trump_rank = players[self.zhuang_jia_id].get_trump_rank() # assumes there is a zhuang jia
        self.suit_played = "none"
        self.discards = []
        self.attacker_points = 0
        # assumes there is a zhuang jia
        print("Round starting: " + players[self.zhuang_jia_id].get_name()
              + " is zhuang jia and the trump rank is " + self.trump_rank)

    # returns number of points attackers earned
    def play_round(self):
        self.deal()
        # todo implement trump ranking (depends on trump rank and trump suit)
        # play out the turns
        # pass in trump info as a dictionary
        info = self.play_turn(self.zhuang_jia_id, self.get_trump_info())
        while len(self.players[0].get_hand()) > 0:
            # todo need id of player starting next turn
            # assumes that play_turn return an info dictionary
            trick_winner = info['trick_winner']
            info = self.play_turn(trick_winner, self.get_trump_info())

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
            print(self.players[current_drawer].name)
            self.players[current_drawer].print_hand()
            self.liang_query(current_drawer)
            current_drawer = (current_drawer + 1) % 4
        # no liang -> flip di pai
        if self.trump_suit == "none":
            self.flip_di_pai()
        # zhuang jia chooses 8 cards for di pai
        self.choose_di_pai()

    def liang_query(self, current_drawer):
        # format is "suit cnt" or "SJo 2" or "BJo 2"
        print("Liang?")
        response = input().split()
        # "n" "no" or nothing means no liang
        if len(response) == 0 or response[0] == "n" or response[0] == "no":
            print("No liang, continuing")
            return
        # check for validity of the response
        if len(response) != 2:
            print("invalid response, continuing")
            return
        if response[1] != "1" and response[1] != "2":
            print("invalid response, continuing")
            return
        if (response[0] == "SJo" or response[0] == "BJo") and response[1] == "2":
            # wu zhu liang
            new_trump_suit = "wu zhu"
            new_trump_suit_cnt = 3
        elif response[0] in Card.suit_map:
            # other liang
            new_trump_suit = response[0]
            new_trump_suit_cnt = int(response[1])
        else:
            print("invalid response, continuing")
            return

        # check whether the liang is valid
        if response[0] == "SJo":
            card_to_check = SMALL_JOKER
            cnt_to_check = 2
        elif response[0] == "BJo":
            card_to_check = BIG_JOKER
            cnt_to_check = 2
        else:
            card_to_check = Card(self.players[0].get_trump_rank(), new_trump_suit)
            cnt_to_check = new_trump_suit_cnt

        if self.players[current_drawer].card_count(card_to_check) >= cnt_to_check:
            if new_trump_suit_cnt > self.trump_suit_cnt:
                print("Set trump suit to: " + new_trump_suit)
                self.trump_suit = new_trump_suit
                self.trump_suit_cnt = new_trump_suit_cnt
            else:
                print("You don't have the cards necessary for that liang")
        else:
            print("You don't have the cards necessary for that liang")

    def cmp_cards(self, a, b):
        # Compares cards in game, with consideration to the first card played
        # returns 1 if a>b, 0 if a=b, and -1 if a<b
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

    def flip_di_pai(self):
        # Flips cards from di pai until the trump rank or joker is hit, and sets the trump suit accordingly
        # Otherwise makes the largest card the trump rank
        largest_rank_suit = "none"
        largest_rank = 1
        rank_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                     'K': 13, 'A': 14}
        for card in self.deck.cards:
            print(card)
            if card.is_big_joker or card.is_small_joker:
                self.trump_suit == "none"
                print("The game is now WuZhu")
                return
            elif card.rank == self.trump_rank:
                self.trump_suit == card.suit
                print("The trump suit is now %s" % card.suit)
                return
            else:
                if rank_dict[card.rank] > largest_rank:
                    largest_rank_suit = card.suit
        self.trump_suit = largest_rank_suit
        print("The trump suit is now %s" % self.trump_suit)
        return

    def choose_di_pai(self):
        for card in self.deck.cards:
            self.players[self.zhuang_jia_id].draw(card)
        while len(self.discards) < 8:
            print("Your discards so far are: ")
            for card in self.discards:
                print(card)
            print("Enter the card that you want to discard. Or, enter \'undo\' to return "
                  "a card from the discard to your hand")
            card_input = pim.get_player_input()
            if card_input.lower() == 'undo':
                print("Enter the card that you want to return to your hand")
                if card_input == "BJo":
                    discard_card = Card('2', 's', is_big_joker=True)
                elif card_input == "SJo":
                    discard_card = Card('2', 's', is_small_joker=True)
                else:
                    discard_card = Card(card_input[:-1], card_input[-1])
                self.discards.remove(discard_card)
            elif pim.is_card(card_input):
                if card_input == "BJo":
                    discard_card = Card('2', 's', is_big_joker=True)
                elif card_input == "SJo":
                    discard_card = Card('2', 's', is_small_joker=True)
                else:
                    discard_card = Card(card_input[:-1], card_input[-1])
                self.discards.append(discard_card)
            else:
                print("Not a valid input. Please enter a valid input")
        for card in self.discards:
            self.players[self.zhuang_jia_id].play(card)

    def get_trump_info(self):
        trumpinfo = {
            'suit': str(self.trump_suit),
            'rank': str(self.trump_rank)
        }
        return trumpinfo

    def is_trump(self, card):
        trumpinfo = self.get_trump_info()
        if card.get_is_joker:
            return True
        if card.get_suit() == trumpinfo['suit']:
            return True
        if card.get_rank() == trumpinfo['rank']:
            return True
        return False

    def get_suit(self, card):
        if self.is_trump(card):
            return "trump"
        else:
            return card.get_suit()

    #returns true if pair1 played greater than pair2
    def pair_gt(self, pair1, pair2):
        if pair1.get_suit() == 'trump' and pair2.get_suit() != 'trump':
            return True
        elif pair2.suit == pair2.get_suit():
            if self.cmp_cards(pair1.get_card(), pair2.get_card()) == 1:
                return True
        else:
            return False

    #FINDS A PAIR ON PRECONDITION THAT ENTIRE HAND IS OF ONE SUIT
    def contains_pair(self, hand):
        suit = self.get_suit(hand[0])
        return self.contains_pair(hand, suit)

    #RETURNS THE NUMBER OF PAIRS IN A CERTAIN SUIT
    def contains_pair(self, hand, suit):
        numpairs = 0
        for card in hand:
            if self.get_suit(card) != suit:
                continue
            for card2 in hand:
                if card is not card2 and card == card2:
                    numpairs += 1
        numpairs /= 2
        return numpairs


    def is_valid_fpi(self, hand):
        #SHUAICHECK
        #FIND BIGGEST TRACTOR
        handtype = []
        card_response = []
        if len(hand) == 2:
            if self.contains_pair(hand) == 1:
                handtype.append('pair')
                card_response.append(Pair(hand[0], self.get_suit(hand[0])))


    def get_first_player_move(self, firstplayer, trumpinfo):
        fp_input = pim.get_player_input()
        #Check if input is a list of valid indeces
        if not pim.is_valid_input(firstplayer, fp_input):
            return {"movecode": "invalid indeces"}
        fp_hand = firstplayer.get_hand()
        suitset = {}
        #Check if is one suit, cursuit
        for each_index in fp_input:
            suitset.add(self.get_suit(firstplayer.get_hand()[each_index]))
        if len(suitset) != 1:
            return {"movecode": "suitset error"}
        else:
            cursuit = suitset[0]
        fpi_hand = []
        for index in fp_input:
            fpi_hand.append(fp_hand[index])
        fpi = self.is_valid_fpi(fpi_hand)





    def play_turn(self, players, sp_index, trumpinfo):
        current_suit = "trump"
        current_type = []
        player_with_biggest_hand = players[sp_index]
        firstplayer = players[sp_index]
        while True:
            fpi = self.get_first_player_move(firstplayer, trumpinfo)


