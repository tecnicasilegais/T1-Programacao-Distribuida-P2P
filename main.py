import random
import peer
import super_peer
import json
import sys
from util import parameter_error_message, display_help

configs = dict()
super_peer_list = []


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
            create_peer()
        case _:
            parameter_error_message()


def create_peer():
    if len(sys.argv) < 3:
        parameter_error_message()
    pass


def create_super_peer():
    global super_peer_list
    for index, peer_name in enumerate(configs):
        super_peer.SuperPeer(peer_name, get_config(index, 'addr'), get_config(index, 'port'),
                            get_config(index, 'next'))
        super_peer_list.append((get_config(index, 'addr'), get_config(index, 'port')))


def read_config():
    global configs
    file = open('config.json')
    configs = json.loads(file.read())


def get_config(index, key):
    global configs
    return list(configs.values())[index][key]


main()
