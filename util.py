import hashlib
import json
import random
import string
from enum import IntEnum, unique


@unique
class MsgType(IntEnum):
    FILE_INFO = 1
    CONNECT = 2
    HEARTBEAT = 3


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


def file_to_hash(file):
    return hashlib.sha256(file.encode()).hexdigest()  # usar outra coisa que gere um hash mais simples


def create_message(msg_type: MsgType, content):
    return json.dumps({
        'type': msg_type.value,
        'contents': content
    })
