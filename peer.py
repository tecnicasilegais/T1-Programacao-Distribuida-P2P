import json
import os
import socket

from util import generate_random_text, file_to_hash, create_message, MsgType


class Peer:

    def __init__(self, addr, port, random_sp_addr):
        self.files = dict()
        self.addr = addr
        self.port = port

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))
        self.random_sp_addr = random_sp_addr
        self.create_files()
        self.send_files_info()

    def send_files_info(self):
        self.send_message(self.random_sp_addr, create_message(MsgType.FILE_INFO, self.files))

    def create_files(self):
        for i in range(2):
            self.files[generate_random_text(7) + '.exe'] = file_to_hash(generate_random_text())

    def send_hash(self, file):
        self.send_message(self.random_sp_addr, file_to_hash(file))

    def send_message(self, random_sp_addr, message):
        self.socket.sendto(message.encode(), random_sp_addr)
