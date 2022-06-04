import socket
import sys
import threading
import random
from socket import *
from time import sleep
from Client import Client
from Lobby import Lobby


class Server:
    # Server Class Constructor
    def __init__(self, max_clients, ip, port):
        print("Creating Server ... ")
        self.socket = None
        self.running = False
        self.max_clients = max_clients
        self.ip = ip
        self.port = port
        self.clients = []
        self.lst_waiting_matchmaking = []
        self.lst_lobby = []
        print("Server created ... waiting for start function ... ")

    # Start Server Function
    # Tries to bind the new socket to the port where the server was established, so it can read data.
    # If failed an error will be printed to console and the program will terminate.
    def start(self):
        print("Server Starting ... ")
        self.socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.socket.bind(("", self.port))
            self.running = True
            print("Server started, initializing threads ... ")
        except socket.error as failed:
            print(f"Failed to Bind Socket .... {failed[0]}:{failed[1]}")
            sys.exit()

        # Try Starting Threads for the server.
        # Start Server Status Thread
        threading.Thread(target=self.server_status).start()
        print("Server Status Thread Started.")

        # Start Listening Thread
        threading.Thread(target=self.listen_for_users).start()
        print("Listening Thread for New Users Started.")

        # Start Matchmaking Thread
        threading.Thread(target=self.matchmaking).start()
        print("Matchmaking Thread Started.")

        print("Server Ready.")

    def server_status(self):
        while self.running:
            sleep(5)
            print(f"Current Number of Online Users: {len(self.clients)}")
            print(f"Current Number of Waiting Matchmaking Users: {len(self.lst_waiting_matchmaking)}")
            print(f"Current Number of Created Lobbies: {len(self.lst_lobby)}")

    def listen_for_users(self):
        while self.running:
            sleep(1 / 1000)
            self.socket.listen(self.max_clients)
            connection, address = self.socket.accept()
            print(f"Connection has been detected ... {address[0]}:{address[1]}. Client operations will begin.")
            client = Client(connection, address, self, random.randint(0, 1000))
            self.clients.append(client)
            client.start()

    def create_new_lobby(self):
        print("New lobby created.")
        lobby = Lobby(random.randint(0, 1000), self)
        lobby.start()
        lobby.add_client(self.lst_waiting_matchmaking.pop())
        self.lst_lobby.append(lobby)

    def matchmaking(self):
        while self.running:
            sleep(1 / 1000)
            if len(self.lst_waiting_matchmaking) > 0:
                if len(self.lst_lobby) == 0:
                    self.create_new_lobby()
                else:
                    for lobby in self.lst_lobby:
                        if lobby.lobby_status == "WAITING":
                            print("Added to an existing lobby")
                            lobby.add_client(self.lst_waiting_matchmaking.pop())
                            break
                        elif lobby == self.lst_lobby[-1]:
                            self.create_new_lobby()
                            break
