import struct
from struct import *
from threading import *
from NetConstant import message_codes, buffer_types


class Client(Thread):
    # Constructor for Class Client
    def __init__(self, connection, address, server, _id):
        Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.server = server
        self.connected = False
        self.id = _id
        self.username = ""

    # Start Client function first waits till the Handshake has been completed. Next It'll read the buffer sent by the
    # client. In case a client disconnect an exception will be thrown and the client will be deleted from registry.
    def run(self):
        self.handshake()
        while self.connected:
            try:
                data = self.connection.recv(2048)
                event = struct.unpack('B', data[:1])[0]

                if event == message_codes["PING"]:
                    self.connection.send(data)
                elif event == message_codes["DISCONNECTION"]:
                    self.disconnect_user()
                elif event == message_codes["MATCHMAKING_START"]:
                    print(f"Matchmaking request received from client {self.address}. Client will be added to queue.")
                    self.server.lst_waiting_matchmaking.append(self)
                    self.connection.send(pack('B', message_codes["MATCHMAKING_RECEIVED"]))
                elif event == message_codes["NETWORK_MATCHMAKING_TIMEOUT"]:
                    print(f"Matchmaking timed out for client {self.address}")
                    self.disconnect_user()
                elif event == message_codes["LOBBY_CONFIRM_PLAYER_CONNECTED_TO_OTHERS_P2P"]:
                    print(f"Updated joining lobby information for client {self.address}")
                    for lobby in self.server.lst_lobby:
                        if self == lobby.temp_waiting_for_approval_player:
                            lobby.clients_in_lobby.append(self)
                            self.connection.send(pack('B', message_codes["SEND_OTHERS_NICKNAME"]))
                            lobby.readyToLetAnotherPlayerJoin = True
            except ConnectionResetError:
                print(f"An error occurred while reading {self.address} data. Client will be deleted from registry.")
                self.disconnect_user()
                break

    # Handshake function is in charge of trying to complete a connection between the server and a client.
    # It'll try to connect three times, if failed then the server will trash the connection and the client object.
    def handshake(self):
        timeout_counter, status_of_handshake = 0, "UNK"
        while timeout_counter < 3 and not self.connected:
            if status_of_handshake == "UNK":
                handshake = pack('B', message_codes["TRYING_HANDSHAKE"])
                self.connection.send(handshake)
                status_of_handshake = "WATNG"
            elif status_of_handshake == "WATNG":
                data = self.connection.recv(1024)
                event = struct.unpack('B', data[:1])[0]
                if event == message_codes["SUCCESS_HANDSHAKE"]:
                    self.connected = True
                    print(f"Handshake of client {self.address} completed. Client is ready for communication.")
                    self.send_string_message_client(message_codes["SEND_SELF_CLIENT_INFO"], 0, f"{self.address[0]}",
                                                    f"{self.address[1]}")
                    break
                else:
                    timeout_counter += 1
        else:
            print(f"Couldn't complete Handshake, Client {self.address} will be deleted from registry.")
            self.disconnect_user()

    # Removes the user from the server after a disconnection event happens
    def disconnect_user(self):
        if self in self.server.lst_waiting_matchmaking:
            self.server.lst_waiting_matchmaking.remove(self)
        self.remove_user_from_lobby()
        self.connected = False
        self.server.clients.remove(self)
        print(f"Disconnected {self.address}.")
        del self

    def remove_user_from_lobby(self):
        for lobby in self.server.lst_lobby:
            if self in lobby.clients_in_lobby:
                lobby.send_all_players_complex_string(self)
                lobby.remove_client(self)
            if self == lobby.temp_waiting_for_approval_player:
                lobby.temp_waiting_for_approval_player = 0
                lobby.readyToLetAnotherPlayerJoin = True

    def send_simple_message_client(self, message):
        self.connection.send(pack('B', message))

    def send_complex_message_client(self, message_id, message_data):
        buffer_type = buffer_types["u8"] + buffer_types["u16"]
        self.connection.send(pack("<" + buffer_type, *[message_id, message_data]))

    # This function will only work when IPv4 strings are involved
    def send_string_message_client(self, message_id, player_number, ip, port):

        # Knowing a regular IPV4 ip address is: 255.255.255.255, a way to avoid dealing with strings is to convert
        # Every divided number. to an actual int and then handling the correct address conversion in gamemaker.

        # Data has this from: MESSAGE_ID, IPp1, IPp2, IPp3, IPp4, Port. All integers.
        ip_in_array = ip.split('.')

        buffer_type = \
            buffer_types["u8"] + buffer_types["u16"] + buffer_types["u16"] + \
            buffer_types["u16"] + buffer_types["u16"] + buffer_types["u16"] + buffer_types["u16"]

        self.connection.send(pack("<" + buffer_type, *[message_id, player_number, int(ip_in_array[0]),
                                                       int(ip_in_array[1]), int(ip_in_array[2]),
                                                       int(ip_in_array[3]), int(port)]))

    def send_team_and_color_dets(self,message_id,color_comb,team_id,team_pos):
        buffer_type = \
            buffer_types["u8"] + buffer_types["u16"] + buffer_types["u16"] + \
            buffer_types["u16"]

        self.connection.send(pack("<" + buffer_type, *[message_id, color_comb, team_id,
                                                       team_pos]))
