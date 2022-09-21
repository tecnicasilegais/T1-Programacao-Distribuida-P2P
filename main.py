import random
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
    peer.Peer(sys.argv[2], int(sys.argv[3]), (sp[1]['addr'], sp[1]['port']))


def create_super_peer():
    interval_size = int(MAX_HASH / len(configs))
    for index, peer_id in enumerate(configs):
        next_peer = get_config(peer_id, 'next')
        hash_interval = (index * interval_size, ((index+1) * interval_size)-1)
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
