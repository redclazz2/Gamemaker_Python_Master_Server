message_codes = {
    "PING": 0,
    "DISCONNECTION": 2,

    "SEND_SELF_CLIENT_INFO": 253,
    "TRYING_HANDSHAKE": 254,
    "SUCCESS_HANDSHAKE": 255,

    "MATCHMAKING_START": 3,
    "MATCHMAKING_RECEIVED": 4,

    "LOBBY_SEND_OTHER_PLAYER_INFO": 9,
    "LOBBY_SEND_TOTAL_PLAYERS_IN_LOBBY": 10,
    "LOBBY_SEND_JOINING_PLAYER_TO_OTHERS": 11,
    "LOBBY_CONFIRM_PLAYER_CONNECTED_TO_OTHERS_P2P": 12,
    "SEND_OTHERS_NICKNAME": 13,

    "LOBBY_READY": 5,
    "LOBBY_JOIN_EMPTY": 6,
    "LOBBY_JOIN_REGULAR": 7,
    "NETWORK_MATCHMAKING_TIMEOUT": 8
}

buffer_types = {
    "u8": "B",
    "u16": "H",
    "string": "s"
}
