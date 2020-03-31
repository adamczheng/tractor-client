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
        hand6 = Hand([Card('8', 'clubs'), Card('8', 'clubs')], cur_round, 'clubs', hand3)

        # Testing pair retrieval
        self.assertListEqual(hand1.pairs, [Pair(cur_round, Card('A', 'clubs'))])
        self.assertListEqual(hand2.pairs, [Pair(cur_round, Card('A', 'clubs'))])
        self.assertListEqual(hand3.pairs, [])
        self.assertListEqual(hand4.pairs, [])
        self.assertListEqual(hand5.pairs, [Pair(cur_round, Card('A', 'spades'))])
        self.assertListEqual(hand6.pairs, [Pair(cur_round, Card('8', 'clubs'))])

        self.assertEqual(hand1.size_compare, 1)
        self.assertEqual(hand2.size_compare, 1)
        self.assertEqual(hand3.size_compare, 0)
        self.assertEqual(hand4.size_compare, 0)
        self.assertEqual(hand5.size_compare, 1)
        self.assertEqual(hand6.size_compare, 0)

        # Testing tractor retrieval
        hand1 = Hand([Card('A', 'spades'), Card('5', 'spades'), Card('5', 'spades'),
                      Card('4', 'spades'), Card('4', 'spades')], cur_round)
        hand2 = Hand([Card('Q', 'spades'), Card('9', 'spades'), Card('9', 'spades'),
                      Card('6', 'spades'), Card('6', 'spades')], cur_round)
        hand3 = Hand([Card('A', 'spades'), Card('A', 'spades'),
                      Card('K', 'spades'), Card('K', 'spades'),
                      Card('5', 'spades'), Card('5', 'spades'),
                      Card('4', 'spades'), Card('4', 'spades')], cur_round)
        hand4 = Hand([Card('A', 'spades'), Card('A', 'spades'),
                      Card('K', 'spades'), Card('K', 'spades'),
                      Card('Q', 'spades'), Card('J', 'spades'),
                      Card('Q', 'spades'), Card('J', 'spades')], cur_round)

        self.assertEqual(hand1.size_compare, 2, "hand1 size compare")
        self.assertEqual(hand2.size_compare, 1, "hand2 size compare")
        self.assertEqual(hand3.size_compare, 2, "hand3 size compare")
        self.assertEqual(hand4.size_compare, 4, "hand4 size compare")
        self.assertEqual(len(hand3.tractors[2]), 2, "hand3 2-tractors")
        self.assertEqual(len(hand4.tractors[2]), 2, "hand4 2-tractors")
        self.assertEqual(len(hand4.tractors[3]), 1, "hand4 3-tractors")
        # TODO: more tractor cases, test init with first_hands
        pass

    def test_check_is_one_suit(self):
        # TODO: all trumps, all non-trump suit, mixed suits
        sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        rank_ids = [0, 0, 0, 0]

        zj_id = 0
        players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
                   Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
        players[zj_id].set_is_zhuang_jia(True)

        cur_round = Round(players)
        hand1 = Hand([Card('A', 'clubs'), Card('A', 'clubs')], cur_round)
        hand2 = Hand([Card('8', 'clubs'), Card('8', 'clubs')], cur_round, 'clubs', hand1)
        print(hand2.first_hand.suit)
        hand3 = Hand([Card('J', 'clubs'), Card('3', 'clubs')], cur_round, 'clubs', hand1)
        hand4 = Hand([Card('5', 'clubs'), Card('10', 'clubs')], cur_round, 'clubs', hand1)

        self.assertTrue(hand1.check_is_one_suit('clubs'))
        self.assertTrue(hand2.check_is_one_suit('clubs'))
        self.assertTrue(hand3.check_is_one_suit('clubs'))
        self.assertTrue(hand4.check_is_one_suit('clubs'))
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
        # TODO: with all tractors, with trumping
        sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        rank_ids = [0, 0, 0, 0]

        zj_id = 0
        players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
                   Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
        players[zj_id].set_is_zhuang_jia(True)

        cur_round = Round(players)
        hand1 = Hand([Card('A', 'spades'), Card('5', 'spades'), Card('5', 'spades'),
                      Card('4', 'spades'), Card('4', 'spades')], cur_round)
        hand2 = Hand([Card('A', 'spades'), Card('Q', 'spades'), Card('J', 'spades'),
                      Card('8', 'spades'), Card('7', 'spades')], cur_round, 'spades', hand1)
        hand3 = Hand([Card('K', 'spades'), Card('J', 'spades'), Card('10', 'spades'),
                      Card('3', 'spades'), Card('6', 'clubs')], cur_round, 'spades', hand1)
        hand4 = Hand([Card('Q', 'spades'), Card('9', 'spades'), Card('9', 'spades'),
                      Card('6', 'spades'), Card('6', 'spades')], cur_round, 'spades', hand1)
        self.assertEqual(hand1.size_compare, 2, "hand1 size compare")
        self.assertEqual(hand4.size_compare, 2, "hand4 size compare")
        self.assertTrue(hand1 > hand2)
        self.assertTrue(hand1 > hand3)
        self.assertTrue(hand1 > hand4)

    def test_single_lead(self):
        # TODO: with trumping, with discards
        pass

    def test_shuai_lead(self):
        pass


if __name__ == '__main__':
    unittest.main()
