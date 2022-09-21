import random
from time import sleep

import peer
import super_peer
import json
import sys

import util
from util import parameter_error_message, display_help, MAX_HASH

configs = dict()


def main():
    print(sys.argv)

    if len(sys.argv) <= 1:
        parameter_error_message()
        return
    filter_args()


def filter_args():
    match sys.argv[1]:
        case '-h':
            display_help()
            return
        case '-sp':
            read_config()
            create_super_peer()
        case '-p':
            read_config()
            create_peer()
        case _:
            parameter_error_message()


def create_peer():
    sp = get_random_sp()  # choose a random super peer to connect
    if len(sys.argv) <= 3:
        parameter_error_message()

    p = peer.Peer(sys.argv[2], int(sys.argv[3]), (sp[1]['addr'], sp[1]['port']))

    while True:
        if p.connected:
            if not p.operation_in_progress:
                print('Peer Operations:')
                print('1 - List Resources')
                print('2 - Download file')

                try:
                    op = int(input())
                    if op == 1:
                        p.operation_in_progress = True
                        p.ask_contents()
                    elif op == 2:
                        p.operation_in_progress = True
                        print('Type the file name')
                        file_name = str(input())
                        p.find_resource(file_name)
                except:
                    continue

            '''
            if len(sys.argv) > 4:
                p.find_resource(sys.argv[4])
            else:
                p.ask_contents()
            break'''
        sleep(1)


def create_super_peer():
    interval_size = int(MAX_HASH / len(configs))
    for index, peer_id in enumerate(configs):
        next_peer = get_config(peer_id, 'next')
        hash_interval = (index * interval_size, ((index + 1) * interval_size) - 1)
        super_peer.SuperPeer(peer_id, get_config(peer_id, 'addr'), get_config(peer_id, 'port'),
                             (get_config(next_peer, 'addr'), get_config(next_peer, 'port')), hash_interval)


def read_config():
    global configs
    file = open('config.json')
    configs = json.loads(file.read())


def get_config(peer_id, key):
    global configs
    return configs[peer_id][key]


def get_random_sp():
    global configs
    return random.choice(list(configs.items()))


main()
