import socket
import threading


class SuperPeer:

    def __init__(self, name, addr, port, next_peer):
        self.addr = addr
        self.name = name
        self.port = port
        self.next_peer = next_peer
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))
        
        self.receive_message_thread = threading.Thread(target=self.receive_message)
        self.receive_message_thread.start()
        print(self.next_peer)

    def receive_message(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            print(data, addr)
