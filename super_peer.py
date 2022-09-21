import json
import socket
import threading
import time


class SuperPeer:

    def __init__(self, name, addr, port, next_peer):
        self.connected_peers: list[(str, int, int)] = list()
        self.table: dict[(str, int), list[str]] = dict()
        self.addr = addr
        self.name = name
        self.port = port
        self.next_peer = next_peer
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))

        self.receive_message_thread = threading.Thread(target=self.receive_message)
        self.receive_message_thread.start()
        print(self.name)
        #self.connected_peers.append(('10.1.1.1', 5000, time.time()))
        self.clear_peer_list_thread = threading.Thread(target=self.clear_peer_list)
        self.clear_peer_list_thread.start()

    def receive_message(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            data_json = json.loads(data.decode('utf-8'))
            if data_json['type'] == 1:
                self.connected_peers.append((addr[0], addr[1], time.time()))
                data_to_remove = list()

                if (addr[0], addr[1]) not in self.table:
                    self.table[(addr[0], addr[1])] = list()

                for k, v in data_json['contents'].items():
                    self.table[(addr[0], addr[1])].append(v)
                    data_to_remove.append(k)

                for k in data_to_remove:
                    data_json['contents'].pop(k)
                
                print(data_json['contents'])
                
                if data_json['contents'] != None:
                    data_json['type'] = 2
                    #self.send_message_for_next(json.dumps(data_json), self.next_peer)

                    
            
            # DECODE RECEIVED PACKET JSON

    def clear_peer_list(self):
        """Checks if there are disconnected peers in the peer list and removes the inactive ones"""
        while True:
            peer_to_remove = list()
            for peer in self.connected_peers:
                if time.time() - peer[2] >= 10:
                    peer_to_remove.append(peer)

            for peer in peer_to_remove:
                self.connected_peers.remove(peer)
                self.clear_peer_hashes(peer)

            time.sleep(1)

    def clear_peer_hashes(self, peer):
        self.table.pop((peer[0], peer[1]), None)
        print('tabela limpa ->',self.table)
        print('peer limpo ->',self.connected_peers)

    def send_message_for_next(self, message, addr):
        self.socket.sendto(message.encode(), addr)