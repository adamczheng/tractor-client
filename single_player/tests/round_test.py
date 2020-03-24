import unittest
from single_player.round import Round
from single_player.player import Player
from single_player.deck import Deck, Card


class RoundTest(unittest.TestCase):
    def test_cmp_cards(self):
        sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        rank_ids = [0, 0, 0, 0]

        zj_id = 0
        players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
                   Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
        players[zj_id].set_is_zhuang_jia(True)

        r = Round(players)
        self.assertTrue(r.cmp_cards(Card('A', 'clubs'), Card('8', 'clubs')) > 0)


if __name__ == '__main__':
    unittest.main()
