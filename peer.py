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
        self.operation_in_progress = False

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

    def find_resource(self, file_name):
        self.send_message(self.sp_addr, create_message(MsgType.FIND_RESOURCE, file_name))

    def receive_message(self):
        """ listen for messages """
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                print('the file host is offline')
                self.operation_in_progress = False
                continue
            data_json = json.loads(data.decode('utf-8'))
            match data_json['type']:
                case MsgType.CONFIRM:
                    self.connected = True
                    self.send_heartbeat_thread.start()
                    self.send_files_info()
                    # self.ask_contents()
                    continue
                case MsgType.ANSWER_CONTENTS:
                    print('received:', data_json, flush=True)
                    self.operation_in_progress = False
                    continue
                case MsgType.ANSWER_RESOURCE:  # answers who has the file i requested
                    print(data_json, flush=True)
                    content = data_json['contents']
                    if not content['found']:
                        print('FILE NOT FOUND', content['file'], flush=True)
                        self.operation_in_progress = False
                    else:
                        print('File Found at peer: ', content['location_ip'], 'port: ', content['location_port'])
                        self.send_message(
                            (content['location_ip'], content['location_port']), create_message(MsgType.GET_RESOURCE, {
                                'file': content['file']
                            }))
                    continue
                case MsgType.GET_RESOURCE:
                    file = data_json['contents']['file']
                    # print('received request for file: ', file, flush=True)
                    found = file in self.files
                    self.send_message(addr, create_message(MsgType.RETURN_RESOURCE, {
                        'file': file,
                        'hash': self.files[file] if found else None,
                        'found': found
                    }))
                    continue
                case MsgType.RETURN_RESOURCE:
                    content = data_json['contents']
                    if not content['found']:
                        print('content not downloaded - FILE NOT FOUND: ', content['file'], flush=True)
                    else:
                        print('Content downloaded: ', content['file'], flush=True)
                        print('The hash is: ', content['hash'], flush=True)
                    self.operation_in_progress = False
                    continue

    def send_message(self, addr, message):
        self.socket.sendto(message.encode(), addr)
