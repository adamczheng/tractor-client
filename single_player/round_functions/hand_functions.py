from single_player.round_functions.pair_functions import Pair
from single_player.round_functions.tractor_functions import Tractor


class Hand(object):

    def __init__(self, cardlist, cur_round, suit='all'):
        self.hand = cardlist
        self.round = cur_round
        self.suit = suit
        self.pairs = []
        self.retrieve_pairs()
        self.tractors = {}
        for i in range(2, 12):
            self.tractors[i] = []

    def __gt__(self, other_hand):
        """
        N
        determine if hand is greater than other hand in the context of the round
        """
        pass

    def __len__(self):
        return len(self.hand)

    def sorted_hand(self):
        return sorted(self.hand, key=self.round.view_value)

    def num_in_suit(self, suit):
        counter = 0
        for each_card in self.hand:
            if self.round.get_suit(each_card) == suit:
                counter += 1
        return counter

    def retrieve_pairs(self):
        sorted_hand = sorted(self.hand, key=self.round.view_value)
        for i in range(len(sorted_hand)-1):
            if sorted_hand[i] == sorted_hand[i+1]:
                self.pairs.append(Pair(self.round, sorted_hand[i]))

    def find_minimum_tractor(self, pair_hand, size):
        """
        Find the minimum tractor in a hand
        :param size:
        :return: an array of length SIZE containing the indexes of the pairs in self.pairs that constitute the smallest
                    tractor of size SIZE in HAND, else None
        """
        pair_indexes = [i.card_value for i in pair_hand]

    def retrieve_tractors(self, pair_hand, size):
        """
        We start off by remembering our original self.hand using the copy method
        The algorithm detects the lowest tractor of size SIZE and appends it to our tractor list.
        Then, we remove the lowest tractor we find of size SIZE.
        We then repeat by slicing out this lowest tractor we find and recursively calling retrieve_tractors.
        We loop from index 0 to (len(self.hand - 2 * size + 1)) to terminate once we cannot find any tractors
        Math check: If len(hand) = 8, we must check index 4 so we use range(8-2*2+1)=range(5)
        At the end, we will reset self.hand by setting it to the copied value

        There is a special case. How do we count a tractor when there is like AdAd2s2s2d2d if we have more 2 non-d?
        :param size: a size n tractor contains 2n cards
        :return:
        """

    def get_num_points(self):
        total = 0
        for card in self.hand:
            if card.get_rank() == '5':
                total += 5
            elif card.get_rank() == '10' or card.get_rank() == 'K':
                total += 10
        return total

    def check_is_one_suit(self, suit):
        for card in self.hand:
            if self.round.get_suit(card) != suit:
                return False
        return True

    def del_indexes(self, index_response):
        for index in sorted(index_response, reverse=True):
            del self.hand[index]

    def subhand_of_suit(self, suit):
        newcardlist = [i for i in self.hand if self.round.get_suit(i) == suit]
        return Hand(newcardlist, self.round, suit)

    def hand_splice(self, start, end):
        return Hand(self.hand[start:end], self.round, self.suit)

    def count_combos(self):
        """
        We only ever use this function on first_hand so we already know that it contains all of the same suit
        We count the total number of singles,
        then the total number of pairs(we don't care if its part of a tractor or not)
        total number of 2 tractors (don't care if its part of a 3+tractor) etc...

        :return:
        """

    def count_singles_of_suit(self, suit):
        return len(self.subhand_of_suit(suit))

    def check_is_legal_move(self):
        return True

