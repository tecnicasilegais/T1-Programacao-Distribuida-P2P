import peer
import superpeer
import json

configs = dict()

def main():
    read_config()
    create_peer()

def create_peer():
    superpeer_number = 0
    while True:
        superpeer_number = int(input("Numero de super nodes:" ))
        if superpeer_number > 0 and superpeer_number <= len(configs):
            break
        else:
            print("Numero invalido")
    for index ,peer_name in enumerate(configs):
        if index <= superpeer_number-1:
            superpeer.SuperPeer(peer_name, get_config(index,"addr"), get_config(index,"port"), get_config(index,"next"))
        else:
            peer.Peer(peer_name, get_config(index,"addr"), get_config(index,"port"), get_config(index,"next"))

def read_config():
    global configs
    file = open("config.json")
    configs = json.loads(file.read())

def get_config(index, key):
    global configs
    return list(configs.values())[index][key]

main()