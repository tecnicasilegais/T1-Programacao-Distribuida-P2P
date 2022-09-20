import socket
import threading
import time


class SuperPeer:

    def __init__(self, name, addr, port, next_peer):
        self.connected_peers: list[(str, int, int)] = list()
        self.addr = addr
        self.name = name
        self.port = port
        self.next_peer = next_peer
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))

        self.receive_message_thread = threading.Thread(target=self.receive_message)
        self.receive_message_thread.start()
        print(self.name)
        self.connected_peers.append(('10.1.1.1', 5000, time.time()))
        self.clear_peer_list()

    def receive_message(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            data_str = data.decode('utf-8')
            print(self.name, data_str, addr)

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
        pass