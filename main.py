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
    for peer_id in configs:
        next_peer = get_config(peer_id, 'next')
        super_peer.SuperPeer(peer_id, get_config(peer_id, 'addr'), get_config(peer_id, 'port'),
                             (get_config(next_peer, 'addr'), get_config(next_peer, 'port')))


def read_config():
    global configs
    file = open('config.json')
    configs = json.loads(file.read())


def get_config(peer_id, key):
    global configs
    return configs[peer_id][key]


main()
