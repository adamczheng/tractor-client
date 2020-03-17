import socket
from _thread import *
import sys
from single_player.round import *
import single_player.round as myConns
from single_player.player import *
import selectors
import types

sel = selectors.DefaultSelector()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(5)
print("Waiting for a connection")
print('Listening on ' + server_ip + ':' + str(port))

sheng_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
rank_ids = [0, 0, 0, 0]

zj_id = 0
players = [Player("Adam", sheng_order[0]), Player("Andrew", sheng_order[0]),
           Player("Alan", sheng_order[0]), Player("Raymond", sheng_order[0])]
players[zj_id].set_is_zhuang_jia(True)

r = Round(players)

def threaded_client(conn):
    # global currentId, pos
    currentId = len(myConns.connections) - 1
    conn.send(str.encode(str(currentId)))
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            curr_player = r.get_current_player()
            # print(curr_player)
            if currentId == curr_player:
                # if reply != 'x': print(reply)
                response = reply.strip('[').strip(']')
                response = [s.strip() for s in response.split(',') if s != '']
                r.set_client_input(response)
                # print(response)
            elif currentId == r.get_last_player() and curr_player != 5:
                response = reply.strip('[').strip(']')
                response = [s.strip() for s in response.split(',') if s != '']
                if response == ['b']:
                    print('take back set')
                    r.set_take_back(True)
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = r.get_data()
            conn.sendall(str.encode(reply))
        except:
            break
    '''
    print("Connection Closed")
    conn.close()
    '''

while len(myConns.connections) < 4:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(threaded_client, (conn,))
    myConns.connections.append(conn)

while True:
    r = Round(players)
    pts = r.play_round()

    if pts == 0:
        # increase trump rank of players[zj_id] and players[(zj_id+2)%4] by 3
        rank_ids[zj_id] += 3
        rank_ids[(zj_id + 2) % 4] += 3
        zj_id = (zj_id + 2) % 4
    elif pts < 40:
        # increase trump rank of players[zj_id] and players[(zj_id+2)%4] by 2
        rank_ids[zj_id] += 2
        rank_ids[(zj_id + 2) % 4] += 2
        zj_id = (zj_id + 2) % 4
    elif pts < 80:
        # increase trump rank of players[zj_id] and players[(zj_id+2)%4] by 1
        rank_ids[zj_id] += 1
        rank_ids[(zj_id + 2) % 4] += 1
        zj_id = (zj_id + 2) % 4
    else:
        num_shengs = (pts - 80) // 40
        # increase trump rank of players[(zj_id+1)%4] and players[(zj_id+3)%4] by num_shengs
        rank_ids[(zj_id + 1) % 4] += num_shengs
        rank_ids[(zj_id + 3) % 4] += num_shengs
        zj_id = (zj_id + 1) % 4

    for i in range(4):
        players[i].set_is_zhuang_jia(False)
        players[i].set_trump_rank(sheng_order[rank_ids[i]])
    players[zj_id].set_is_zhuang_jia(True)

    if rank_ids[zj_id] >= len(sheng_order):
        print(players[zj_id].get_name() + ' and ' + players[(zj_id + 2) % 4].get_name() + 'win!')
        break

'''
data = client_conns[0].recv(2048)
reply = data.decode('utf-8')
if reply == 'x':
    print("received x")
else:
    reply = "y"
client_conns[0].sendall(str.encode(reply))


def get_player_input(self):
    # just player indexes, check if integerse
    response = input().split()
    integer_list = [s for s in response if s.isdigit()]
    return list(map(int, integer_list))


def is_valid_input(self, player, response):
    if len(set(response)) != len(response):
        return False
    for each_index in response:
        if int(each_index) < 0 or int(each_index) >= len(player.get_hand()):
            return False
    return True
'''