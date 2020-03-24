import unittest
from single_player.round_functions.hand_functions import Hand
from single_player.round import Round
from single_player.player import Player
from single_player.deck import Deck, Card
from single_player.round_functions.pair_functions import Pair


class HandTest(unittest.TestCase):

    def test_init(self):
        sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        rank_ids = [0, 0, 0, 0]

        zj_id = 0
        players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
                   Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
        players[zj_id].set_is_zhuang_jia(True)

        cur_round = Round(players)
        hand1 = Hand([Card('A', 'clubs'), Card('A', 'clubs')], cur_round)
        hand2 = Hand([Card('A', 'clubs'), Card('K', 'clubs'), Card('A', 'clubs')], cur_round)
        hand3 = Hand([Card('A', 'clubs'), Card('K', 'clubs')], cur_round)
        hand4 = Hand([Card('A', 'clubs'), Card('A', 'spades')], cur_round)
        hand5 = Hand([Card('A', 'clubs'), Card('A', 'spades'), Card('A', 'spades')], cur_round)
        self.assertListEqual(hand1.pairs, [Pair(cur_round, Card('A', 'clubs'))])
        self.assertListEqual(hand2.pairs, [Pair(cur_round, Card('A', 'clubs'))])
        self.assertListEqual(hand3.pairs, [])
        self.assertListEqual(hand4.pairs, [])
        self.assertListEqual(hand5.pairs, [Pair(cur_round, Card('A', 'spades'))])
        # TODO: test tractor retrieval
        pass

    def test_check_is_one_suit(self):
        # TODO: all trumps, all non-trump suit, mixed suits
        pass

    def test_pair_lead(self):
        sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        rank_ids = [0, 0, 0, 0]

        zj_id = 0
        players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
                   Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
        players[zj_id].set_is_zhuang_jia(True)

        cur_round = Round(players)
        hand1 = Hand([Card('A', 'clubs'), Card('A', 'clubs')], cur_round)
        hand2 = Hand([Card('8', 'clubs'), Card('8', 'clubs')], cur_round, 'clubs', hand1)
        hand3 = Hand([Card('J', 'clubs'), Card('3', 'clubs')], cur_round, 'clubs', hand1)
        hand4 = Hand([Card('5', 'clubs'), Card('10', 'spades')], cur_round, 'clubs', hand1)
        self.assertTrue(hand1 > hand2)
        self.assertTrue(hand1 > hand3)
        self.assertTrue(hand1 > hand4)

    def test_tractor_lead(self):
        # TODO: with all tractors, with some random, with trumping
        pass

    def test_single_lead(self):
        # TODO: with trumping, with discards
        pass

    def test_shuai_lead(self):
        pass


if __name__ == '__main__':
    unittest.main()
