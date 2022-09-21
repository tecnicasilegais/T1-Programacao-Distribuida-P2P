import json
import os
import socket
import threading
from time import sleep

from util import generate_random_text, generate_hash, create_message, MsgType


class Peer:

    def __init__(self, addr, port, sp_addr):
        self.files: dict[str, int] = dict()
        self.addr = addr
        self.port = port
        self.connected = False

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))

        self.receive_message_thread = threading.Thread(target=self.receive_message)
        self.receive_message_thread.start()

        self.send_heartbeat_thread = threading.Thread(target=self.heartbeat)

        self.sp_addr = sp_addr
        self.create_files()
        self.connect()

    def send_files_info(self):
        self.send_message(self.sp_addr, create_message(MsgType.FILE_INFO, self.files))

    def create_files(self):
        for i in range(2):
            self.files[generate_random_text(15) + '.exe'] = generate_hash()

    def connect(self):
        self.send_message(self.sp_addr, create_message(MsgType.CONNECT, None))

    def heartbeat(self):
        """sends heartbeat messages to super node every 5 seconds"""
        while True:
            sleep(5)
            self.send_message(self.sp_addr, create_message(MsgType.HEARTBEAT, None))

    def ask_contents(self):
        self.send_message(self.sp_addr, create_message(MsgType.ASK_CONTENTS, None))

    def receive_message(self):
        """ listen for messages """
        while True:
            data, addr = self.socket.recvfrom(1024)
            data_json = json.loads(data.decode('utf-8'))
            match data_json['type']:
                case MsgType.CONFIRM:
                    self.connected = True
                    self.send_heartbeat_thread.start()
                    self.send_files_info()
                    self.ask_contents()
                    continue
                case MsgType.ANSWER_CONTENTS:
                    print('received:', data_json, flush=True)
                    continue

    def send_message(self, addr, message):
        self.socket.sendto(message.encode(), addr)
