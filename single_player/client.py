import pygame
import single_player.round as myConns
from time import sleep
import socket
from single_player.network import Network
from math import *


# todo: gui abstraction, turn indication

class TractorClient():
    # create dict of each card image
    card_height = 155
    card_width = 100
    small_card_height = 100
    small_card_width = 65
    deck_dict = {}
    small_deck_dict = {}
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['C', 'D', 'H', 'S']
    suit_map = {'C': '\u2663', 'D': '\u2666', 'H': '\u2665', 'S': '\u2660'}
    for rank in ranks:
        for s in suits:
            card_key = rank + suit_map[s]
            card_file = "cards_jpeg\\" + rank + s + ".jpg"
            my_card = pygame.transform.scale(pygame.image.load(card_file), (card_width, card_height))
            deck_dict[card_key] = my_card
            my_card = pygame.transform.scale(pygame.image.load(card_file), (small_card_width, small_card_height))
            small_deck_dict[card_key] = my_card
    deck_dict['BJo'] = pygame.transform.scale(pygame.image.load("cards_jpeg\\BJo.jpg"), (card_width, card_height))
    deck_dict['SJo'] = pygame.transform.scale(pygame.image.load("cards_jpeg\\SJo.jpg"), (card_width, card_height))
    small_deck_dict['BJo'] = pygame.transform.scale(pygame.image.load("cards_jpeg\\BJo.jpg"),
                                                    (small_card_width, small_card_height))
    small_deck_dict['SJo'] = pygame.transform.scale(pygame.image.load("cards_jpeg\\SJo.jpg"),
                                                    (small_card_width, small_card_height))

    card_back_vert = pygame.transform.scale(pygame.image.load("cards_jpeg\\Red_back.jpg"),
                                            (small_card_width, small_card_height))
    card_back_hor = pygame.transform.rotate(
        pygame.transform.scale(pygame.image.load("cards_jpeg\\Red_back.jpg"), (small_card_width, small_card_height)),
        90)
    play_btn = pygame.transform.scale(pygame.image.load("cards_jpeg\\play_button.jpg"), (120, 65))
    clear_btn = pygame.transform.scale(pygame.image.load("cards_jpeg\\clear_button.jpg"), (120, 65))
    white_rect = pygame.Surface((card_width, card_height))
    white_rect.fill((0, 0, 0, 255))

    def __init__(self, test=False):

        pygame.init()
        self.width, self.height = 900, 600

        # initialize the screen
        self.screen = pygame.display.set_mode((self.width, self.height))

        # initialize pygame clock
        self.clock = pygame.time.Clock()
        if test:
            self.playerID = 0
        else:
            self.net = Network(False)
            self.playerID = int(self.net.getID())
            pygame.display.set_caption("Client " + str(self.playerID))
        self.data = None
        self.card_indices = []
        self.current_player = 5
        self.turn_positions = {}
        self.position_keys = [i % 4 for i in range(self.playerID, self.playerID + 4)]
        self.position_values = [(450, 600), (900, 250), (450, 0), (0, 250)]
        for i in range(len(self.position_keys)):
            self.turn_positions[self.position_keys[i]] = self.position_values[i]
        self.user_rects = []

    def draw_board(self):
        self.draw_hands()
        self.draw_buttons()
        self.draw_turn()
        # self.draw_cleared()
        self.draw_deck()
        self.draw_stats()

    def draw_stats(self):
        pass
        # draws score, trump suit
        white = (255, 255, 255)
        my_font = pygame.font.SysFont('comicsansmc', 20)
        score = my_font.render('Score: ' + self.data[15], True, white)
        trump = my_font.render('Trump: ' + self.data[16], True, white)
        self.screen.blit(score, [110, 5])
        self.screen.blit(trump, [110, 25])

    def draw_turn(self):
        curr_data = int(self.data[17])
        if curr_data < 5:
            self.current_player = curr_data
        if self.current_player < 5:
            pygame.draw.circle(self.screen, (200, 0, 0), self.turn_positions[self.current_player], 45)

    def draw_hands(self):
        pass
        # draws all hands with only your own showing
        # gets hands of all players
        player_hands = []
        played_cards = []
        for i in range(4):
            player_hands.append(self.data[i * 3 + 1])
            played_cards.append(self.data[i * 3 + 2])
        user_hand = player_hands[self.playerID % 4]
        right_hand = player_hands[(self.playerID + 1) % 4]
        across_hand = player_hands[(self.playerID + 2) % 4]
        left_hand = player_hands[(self.playerID + 3) % 4]
        user_played = played_cards[self.playerID % 4]
        right_played = played_cards[(self.playerID + 1) % 4]
        across_played = played_cards[(self.playerID + 2) % 4]
        left_played = played_cards[(self.playerID + 3) % 4]

        self.user_rects = [self.play_btn.get_rect().move(772, 465), self.clear_btn.get_rect().move(772, 532)]
        # draw hands
        if len(user_hand) > 0:
            left_coord = self.width // 2 - (round(0.22 * self.card_width) * (len(user_hand) - 1) + self.card_width) / 2
            for card_index in range(len(user_hand)):
                offset = 25 if card_index in self.card_indices else 0
                if card_index < len(user_hand) - 1:
                    self.screen.blit(self.white_rect, [left_coord + 22 * (card_index), 445 - offset],
                                     area=self.white_rect.get_rect(), special_flags=4)
                    self.user_rects.append(self.white_rect.get_rect().move(left_coord + 22 * (card_index), 445 - offset))
                    self.screen.blit(self.deck_dict[user_hand[card_index]],
                                     [left_coord + 22 * (card_index), 445 - offset],
                                     area=self.deck_dict[user_hand[card_index]].get_rect(), special_flags=0)
                else:
                    self.screen.blit(self.white_rect, [left_coord + 22 * (card_index), 445 - offset],
                                     area=self.white_rect.get_rect(), special_flags=4)
                    self.user_rects.append(
                        self.white_rect.get_rect().move(left_coord + 22 * (card_index), 445 - offset))
                    self.screen.blit(self.deck_dict[user_hand[card_index]],
                                     [left_coord + 22 * (card_index), 445 - offset],
                                     area=self.deck_dict[user_hand[card_index]].get_rect(), special_flags=0)
        if len(across_hand) > 0:
            left_coord = self.width // 2 - (15 * (len(across_hand)) - 1 + 65) / 2
            for card_index in range(len(across_hand)):
                if card_index < len(across_hand) - 1:
                    self.screen.blit(self.card_back_vert, [left_coord + 15 * (card_index), 0],
                                     area=pygame.Rect(0, 0, 15, 100), special_flags=0)
                else:
                    self.screen.blit(self.card_back_vert, [left_coord + 15 * (card_index), 0],
                                     area=None, special_flags=0)
        if len(left_hand) > 0:
            left_coord = 250 - (15 * (len(left_hand)) - 1 + 65) / 2
            for card_index in range(len(left_hand)):
                if card_index < len(left_hand) - 1:
                    self.screen.blit(self.card_back_hor, [0, left_coord + 15 * (card_index)],
                                     area=pygame.Rect(0, 0, 100, 15), special_flags=0)
                else:
                    self.screen.blit(self.card_back_hor, [0, left_coord + 15 * (card_index)],
                                     area=None, special_flags=0)
        if len(right_hand) > 0:
            left_coord = 250 - (15 * (len(right_hand)) - 1 + 65) / 2
            for card_index in range(len(right_hand)):
                if card_index < len(right_hand) - 1:
                    self.screen.blit(self.card_back_hor, [800, left_coord + 15 * (card_index)],
                                     area=pygame.Rect(0, 0, 100, 15), special_flags=0)
                else:
                    self.screen.blit(self.card_back_hor, [800, left_coord + 15 * (card_index)], area=None,
                                     special_flags=0)

        # draw played cards
        if len(user_played) > 0:
            left_coord = self.width // 2 - (15 * (len(user_played) - 1) + 65) / 2
            for card_index in range(len(user_played)):
                if card_index < len(user_played) - 1:
                    self.screen.blit(self.small_deck_dict[user_played[card_index]],
                                     [left_coord + 15 * (card_index), 288],
                                     area=pygame.Rect(0, 0, 15, 100), special_flags=0)
                else:
                    self.screen.blit(self.small_deck_dict[user_played[card_index]],
                                     [left_coord + 15 * (card_index), 288], area=None,
                                     special_flags=0)
        if len(across_played) > 0:
            left_coord = self.width // 2 - (15 * (len(across_played) - 1) + 65) / 2
            for card_index in range(len(across_played)):
                if card_index < len(across_played) - 1:
                    self.screen.blit(self.small_deck_dict[across_played[card_index]],
                                     [left_coord + 15 * (card_index), 107],
                                     area=pygame.Rect(0, 0, 15, 100), special_flags=0)
                else:
                    self.screen.blit(self.small_deck_dict[across_played[card_index]],
                                     [left_coord + 15 * (card_index), 107],
                                     area=None, special_flags=0)
        if len(left_played) > 0:
            left_coord = 108
            for card_index in range(len(left_played)):
                if card_index < len(left_played) - 1:
                    self.screen.blit(self.small_deck_dict[left_played[card_index]],
                                     [left_coord + 15 * (card_index), 197],
                                     area=pygame.Rect(0, 0, 15, 100), special_flags=0)
                else:
                    self.screen.blit(self.small_deck_dict[left_played[card_index]],
                                     [left_coord + 15 * (card_index), 197],
                                     area=None, special_flags=0)
        if len(right_played) > 0:
            left_coord = 792 - (15 * (len(right_played) - 1) + 65)
            for card_index in range(len(right_played)):
                if card_index < len(right_played) - 1:
                    self.screen.blit(self.small_deck_dict[right_played[card_index]],
                                     [left_coord + 15 * (card_index), 197],
                                     area=pygame.Rect(0, 0, 15, 100), special_flags=0)
                else:
                    self.screen.blit(self.small_deck_dict[right_played[card_index]],
                                     [left_coord + 15 * (card_index), 197], area=None, special_flags=0)

    def draw_deck(self):
        if self.data[13] == 'True':
            self.screen.blit(self.card_back_vert, [35, 481])

    def draw_cleared(self):
        if self.data[12] == 'True':
            self.screen.blit(self.card_back_vert, [417, 222])

    def draw_buttons(self):
        self.screen.blit(self.play_btn, [772, 465])
        self.screen.blit(self.clear_btn, [772, 532])

    def update(self, test=False):
        # make the game 60 fps
        self.clock.tick(60)

        # clear the screen
        self.screen.fill(0)

        # draws board over cleared screen
        self.draw_board()

        if not test:
            # take input
            click = None
            for event in pygame.event.get():
                # quit if the quit button was pressed
                if event.type == pygame.QUIT:
                    myConns.connections[self.playerID].close()
                    exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    click = event.pos
                elif event.type == pygame.KEYUP:
                    click = event.key

            self.data = self.parse_data(self.send_data(click))

        # update the screen
        pygame.display.flip()

    def send_data(self, position):
        reply = self.net.send('x')
        if not position:
            return reply
        if type(position) == int:
            if position == 32:
                print('space')
                return self.net.send('space')
            if position == 98:
                print('b')
                return self.net.send('b')
            return reply
        player_hand = self.data[self.playerID * 3 + 1]
        left_offset = (22 * (len(player_hand) - 1) + 100) / 2
        for i in range(len(self.user_rects) - 1, -1, -1):
            if self.user_rects[i].collidepoint(position):
                if i > 1:
                    click_index = i - 2
                    if click_index in self.card_indices:
                        self.card_indices.remove(click_index)
                    else:
                        self.card_indices.append(click_index)
                elif i == 1:
                    # clear button
                    self.card_indices.clear()
                    print('clear')
                else:
                    # play button
                    if self.card_indices:
                        reply = self.net.send(str(self.card_indices))
                        self.card_indices.clear()
                break
        return reply

    def parse_data(self, response):
        if not response:
            return self.data
        data = [0, None, None, 1, None, None, 2, None, None, 3, None, None, None, None, None, None, None, None]
        split_data = response.split(':')
        data[1] = self.make_list(split_data[1]) # player 0 hand list
        data[2] = self.make_list(split_data[2]) # player 0 played list
        data[4] = self.make_list(split_data[4]) # 1 hand
        data[5] = self.make_list(split_data[5]) # 1 played
        data[7] = self.make_list(split_data[7]) # 2 hand
        data[8] = self.make_list(split_data[8]) # 2 played
        data[10] = self.make_list(split_data[10]) # 3 hand
        data[11] = self.make_list(split_data[11]) # 3 played
        data[12] = str(split_data[12]) # clear boolean
        data[13] = str(split_data[13]) # di pai boolean
        data[14] = str(split_data[14]) # game start boolean
        data[15] = str(split_data[15]) # attacker points int
        data[16] = str(split_data[16]) # trump suit str
        data[17] = str(split_data[17]) # current player int
        return data

    def make_list(self, list_in):
        list_out = list_in.strip('[').strip(']')
        list_out = [s.strip() for s in list_out.split(',') if s != '']
        return list_out

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data


if __name__ == '__main__':
    myClient = TractorClient()
    '''
    while True:
        for event in pygame.event.get():
            # quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
        if not myClient.get_data():
            myClient.set_data(myClient.parse_data(myClient.send_data((0,0))))
            continue
        break
    print('starting game')
    '''
    while 1:
        if myClient.get_data() and myClient.get_data()[14] == "True":
            myClient.update()
        else:
            for event in pygame.event.get():
                # quit if the quit button was pressed
                if event.type == pygame.QUIT:
                    exit()
            myClient.set_data(myClient.parse_data(myClient.send_data(None)))
