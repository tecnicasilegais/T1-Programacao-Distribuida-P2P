import socket


class SuperPeer:

    def __init__(self,name, addr, port, next_peer):
        self.addr = addr
        self.name = name
        self.port = port
        self.next_peer = next_peer
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))