import peer
import super_peer
import json
import sys
from util import parameter_error_message, display_help

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
            create_peer()
        case _:
            parameter_error_message()


def create_peer():
    peer.Peer('peer1',sys.argv[2], int(sys.argv[3]),("127.0.0.100", 4941))


def create_super_peer():
    for index, peer_name in enumerate(configs):
        super_peer.SuperPeer(peer_name, get_config(index, 'addr'), get_config(index, 'port'),
                            get_config(index, 'next'))

def read_config():
    global configs
    file = open('config.json')
    configs = json.loads(file.read())


def get_config(index, key):
    global configs
    return list(configs.values())[index][key]


main()
