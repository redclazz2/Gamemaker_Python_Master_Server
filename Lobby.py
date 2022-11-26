import random
import time
from struct import *
from threading import *
from NetConstant import message_codes
from collections import deque


class Lobby(Thread):
    # Constructor for Class Lobby
    def __init__(self, lobby_id, server):
        Thread.__init__(self)
        self.lobby_id = lobby_id
        self.server = server
        self.clients_in_lobby = []

        #FOR DEBUG
        self.max_clients = 1

        self.clients_t1 = []
        self.clients_t2 = []

        self.clients_waiting_to_join = deque()
        self.temp_waiting_for_approval_player = 0
        self.lobby_status = "WAITING"
        self.availableToClose = False
        self.sentReady = False
        self.readyToLetAnotherPlayerJoin = True

    def run(self):
        while self.server.running:
            if len(self.clients_in_lobby) == 0 and self.availableToClose:
                self.server.lst_lobby.remove(self)
                del self
                break
            elif len(self.clients_in_lobby) == self.max_clients and not self.sentReady:
                self.lobby_status = "READY"
                self.send_simple_message_all_lobby_clients(message_codes["LOBBY_READY"])
                self.sentReady = True

            elif 0 < len(self.clients_in_lobby) < self.max_clients:
                self.lobby_status = "WAITING"

            if len(self.clients_waiting_to_join) > 0 and self.readyToLetAnotherPlayerJoin:
                self.process_for_client_to_join(self.clients_waiting_to_join.popleft())
                self.readyToLetAnotherPlayerJoin = False

    def add_client(self, client):
        if client not in self.clients_in_lobby:
            if len(self.clients_in_lobby) == 0:
                time.sleep(1/100)
                client.send_complex_message_client(message_codes["LOBBY_JOIN_EMPTY"], self.lobby_id)
                self.clients_in_lobby.append(client)
                self.availableToClose = True
            else:
                client.send_complex_message_client(message_codes["LOBBY_JOIN_REGULAR"], self.lobby_id)
                self.let_others_communicate(client)
                self.clients_waiting_to_join.append(client)

    def remove_client(self, client):
        self.clients_in_lobby.remove(client)

    def send_all_players_complex_string(self, _client):
        for client in self.clients_in_lobby:
            if client != _client:
                client.send_string_message_client(message_codes["LOBBY_SEND_DISCONNECTED_PLAYER_INFO"], 0,
                                                  _client.address[0], _client.address[1])

    def send_simple_message_all_lobby_clients(self, message):
        for client in self.clients_in_lobby:
            client.connection.send(pack('B', message))

    def let_others_communicate(self, _client):
        for client in self.clients_in_lobby:
            client.send_string_message_client(message_codes["LOBBY_SEND_JOINING_PLAYER_TO_OTHERS"], 0,
                                              _client.address[0], _client.address[1])

    def process_for_client_to_join(self, client):
        self.temp_waiting_for_approval_player = client
        client.send_complex_message_client(message_codes["LOBBY_SEND_TOTAL_PLAYERS_IN_LOBBY"],
                                           len(self.clients_in_lobby))
        time.sleep(1/10)
        for i in range(0, len(self.clients_in_lobby)):
            time.sleep(1 / 100)
            client.send_string_message_client(message_codes["LOBBY_SEND_OTHER_PLAYER_INFO"], i,
                                              self.clients_in_lobby[i].address[0],
                                              self.clients_in_lobby[i].address[1])
            print("Sent!")

    def sort_for_teams(self):
        color_combinator = random.randint(1, 4)
        counter = 0

        players_to_organize = self.clients_in_lobby.copy()

        #Randomly sort a set amount of players in two teams.
        controller = True
        current_middle_ground = len(self.clients_in_lobby) / 2
        while(controller and len(players_to_organize) > 0):
            rnd = random.randint(1,2)
            if(rnd == 1 and len(self.clients_t1) < current_middle_ground):
                self.clients_t1.append(players_to_organize.pop())
            elif(len(self.clients_t2) < current_middle_ground):
                self.clients_t2.append(players_to_organize.pop())
            else:
                controller = False

        for cliente in self.clients_t1:
            cliente.send_team_and_color_dets(message_codes["SEND_TEAM_AND_COLORS_DET"],color_combinator,1,counter)
            counter += 1

        counter = 0

        for cliente in self.clients_t2:
            cliente.send_team_and_color_dets(message_codes["SEND_TEAM_AND_COLORS_DET"],color_combinator,2,counter)
            counter += 1
