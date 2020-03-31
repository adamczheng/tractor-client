from single_player.round_functions.pair_functions import Pair
from single_player.round_functions.tractor_functions import Tractor


class Hand(object):

    def __init__(self, cardlist, cur_round, suit='all', first=None):
        self.hand = sorted(cardlist, key=cur_round.view_value)
        # print(self.hand)
        self.round = cur_round
        self.pairs = []
        self.retrieve_pairs()
        self.pairs.sort()
        self.tractors = {}
        for i in range(2, 13):
            self.tractors[i] = []
        self.retrieve_tractors()
        self.sort_tractors()
        self.first_hand = first
        if first == None:
            self.first_hand = self
            self.suit = cur_round.get_suit(self.hand[0])
            self.size_compare = 0
            if len(self.pairs) > 0:
                self.size_compare = 1
            for i in range(12, 1, -1):
                if len(self.tractors[i]) > 0:
                    self.size_compare = i
                    break
        else:
            self.size_compare = self.first_hand.size_compare
            self.suit = suit

    def __gt__(self, other_hand):
        """
        N
        determine if hand is greater than other hand in the context of the round
        """
        first_suit = self.round.get_suit(self.hand[0])
        if not self.check_is_one_suit(first_suit) or not (first_suit == self.first_hand.suit or first_suit == 'trump'):
            return False
        if not len(self.pairs) >= len(self.first_hand.pairs):
            return False
        for tractor_length in range(2, 13):
            if not len(self.tractors[tractor_length]) >= len(self.first_hand.tractors[tractor_length]):
                return False
        if self.size_compare == 0:
            if self.round.cmp_cards(self.hand[-1], other_hand.hand[-1]) > 0:
                return True
        elif self.size_compare == 1:
            if len(self.pairs) > len(other_hand.pairs) or self.pairs[-1] > other_hand.pairs[-1]:
                return True
        else:
            if len(self.tractors[self.size_compare]) > len(other_hand.tractors[self.size_compare]) \
                    or self.tractors[self.size_compare][-1] > other_hand.tractors[self.size_compare][-1]:
                return True
        return False

    def __len__(self):
        return len(self.hand)

    def num_in_suit(self, suit):
        counter = 0
        for each_card in self.hand:
            if self.round.get_suit(each_card) == suit:
                counter += 1
        return counter

    def retrieve_pairs(self):
        for i in range(len(self.hand) - 1):
            if self.hand[i] == self.hand[i+1]:
                self.pairs.append(Pair(self.round, self.hand[i]))

    def find_minimum_tractor(self, pair_hand, size):
        """
        Find the minimum tractor in a hand
        :param size:
        :return: an array of length SIZE containing the indexes of the pairs in self.pairs that constitute the smallest
                    tractor of size SIZE in HAND, else None
        """
        pair_indexes = [i.card_value for i in pair_hand]

    def retrieve_tractors(self):
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
        pair_values = [i.card_value for i in self.pairs]
        for i in range(2, 13):
            current_index = i-1
            while current_index < len(pair_values):
                is_tractor = True
                for j in range(current_index, current_index - i + 1, -1):
                    if pair_values[j] != pair_values[j-1] + 1:
                        current_index += 1
                        is_tractor = False
                        break
                if is_tractor:
                    self.tractors[i].append(Tractor(pair_values[current_index], i))
                    current_index += i

    def sort_tractors(self):
        for length in range(2, 13):
            self.tractors[length].sort()

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

