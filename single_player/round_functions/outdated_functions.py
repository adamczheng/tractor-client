"""
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
"""