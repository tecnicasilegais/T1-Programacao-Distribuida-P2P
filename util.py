import json
import random
import string
import numpy as np
from enum import IntEnum, unique

MAX_HASH = 1000000000


@unique
class MsgType(IntEnum):
    CONNECT = 0
    CONFIRM = 1
    FILE_INFO = 2
    HEARTBEAT = 3
    SPREAD_HASH = 4  # send hash to the correct super node in the ring
    SPREAD_CLEAR = 5  # send notice that some node disconnected, we should remove its hashes
    ASK_CONTENTS = 6  # peer asks for content list
    SPREAD_ASK_CONTENTS = 7  # super peer spreads the request
    ANSWER_CONTENTS = 8  # super peer returns the contents


def display_help():
    print('to execute in Super-Peer mode, run with:')
    print('\t\t python program.py -sp')
    print('to execute in peer mode, run with:')
    print('\t\t python program.py -p <ip> <port>')


def parameter_error_message():
    print('Error: incorrect parameters. Run with -h for support')


def generate_random_text(size=100):
    size = random.randint(1, size)
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))


def generate_hash():
    return np.random.randint(0, MAX_HASH)
    # hashlib.sha256(file.encode()).hexdigest()  # usar outra coisa que gere um hash mais simples


def create_message(msg_type: MsgType, content):
    return json.dumps({
        'type': msg_type.value,
        'contents': content
    })
