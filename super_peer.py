import json
import socket
import threading
import time
from typing import Any

from util import MsgType, create_message


class SuperPeer:

    def __init__(self, name, addr, port, next_peer, hash_range):
        # (ip, port), timestamp
        self.connected_peers: dict[(str, int), float] = dict()
        # (hash), (ip, port, name)
        self.table: dict[int, (str, int, str)] = dict()
        self.addr = addr
        self.name = name
        self.port = port
        self.next_peer = next_peer
        self.hash_range = hash_range
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))
        self.receive_message_thread = threading.Thread(target=self.receive_message)
        self.receive_message_thread.start()

        self.clear_peer_list_thread = threading.Thread(target=self.clear_peer_list)
        self.clear_peer_list_thread.start()

        self.print_table_thread = threading.Thread(target=self.print_table)
        self.print_table_thread.start()

        print(self.name, '- hash range starts at', self.hash_range[0], 'and ends at', self.hash_range[1])

    def receive_message(self):
        """ listen for messages """
        while True:
            data, addr = self.socket.recvfrom(1024)
            data_json = json.loads(data.decode('utf-8'))

            match data_json['type']:
                case MsgType.CONNECT:
                    self.connect(addr)
                    continue
                case MsgType.FILE_INFO:
                    self.receive_file_info(data_json, addr)
                    continue
                case MsgType.HEARTBEAT:
                    self.heartbeat(addr)
                    continue
                case MsgType.SPREAD_HASH:
                    self.receive_hashes_from_sp(data_json)
                    continue
                case MsgType.SPREAD_CLEAR:
                    self.spread_clear_hashes(data_json)
                    continue
                case MsgType.ASK_CONTENTS:
                    self.init_content_recover(addr)
                case MsgType.SPREAD_ASK_CONTENTS:
                    self.continue_content_recover(data_json)
                    continue
                case MsgType.FIND_RESOURCE:
                    self.init_find_resource(addr, data_json)
                    continue
                case MsgType.SPREAD_FIND_RESOURCE:
                    self.continue_find_resource(data_json)

    def connect(self, addr):
        """Connects to a new peer"""
        self.connected_peers[addr] = time.time()
        print(self.name, '- Peer connected', addr[0], addr[1])
        self.send_message(addr, create_message(MsgType.CONFIRM, None))

    def heartbeat(self, addr):
        """receives heartbeats from peers and renews their connection"""
        if addr in self.connected_peers:
            self.connected_peers[addr] = time.time()

    def receive_file_info(self, data_json, addr):
        """receive file info from a new joined peer"""
        if addr not in self.connected_peers:
            return

        spread_hash_values = dict()

        for k, v in data_json['contents'].items():
            if self.hash_range[0] <= v <= self.hash_range[1]:
                self.table[v] = (addr[0], addr[1], k)
                # print('rci', self.name, self.table)
            else:
                spread_hash_values[v] = {
                    'address': addr[0],
                    'port': addr[1],
                    'name': k
                }
        if any(spread_hash_values):
            self.send_message(self.next_peer, create_message(MsgType.SPREAD_HASH, spread_hash_values))

    def receive_hashes_from_sp(self, data_json):
        """receives hashes from other super peers and checks if it's within this Super Peer range. If it's not,
        it spreads the hashes again """
        rcv_table = data_json['contents']
        spread_hash_values = dict()
        # print('receiving data', self.name, self.hash_range)
        for k in rcv_table:
            # print(k, rcv_table[k])
            if self.hash_range[0] <= int(k) <= self.hash_range[1]:
                self.table[int(k)] = (rcv_table[k]['address'], rcv_table[k]['port'], rcv_table[k]['name'])
                # print(self.name, self.table)
            else:
                # print('spread again')
                spread_hash_values[k] = rcv_table[k]

        if any(spread_hash_values):
            self.send_message(self.next_peer, create_message(MsgType.SPREAD_HASH, spread_hash_values))

    def spread_clear_hashes(self, data_json):
        """if it's not the origin, remove the peer hashes and spread the message to the next SP in the token ring"""
        if self.name == data_json['contents']['origin']:
            return

        peer = (data_json['contents']['address'], data_json['contents']['port'])
        self.clear_peer_hashes(peer)
        self.send_message(self.next_peer, create_message(MsgType.SPREAD_CLEAR, data_json['contents']))

    def init_content_recover(self, peer_addr):
        """Peer asked this Super Peer to list all the available resources in the system"""
        files = [name for _, (_, _, name) in self.table.items()]
        # print('init', self.name, files)
        self.send_message(self.next_peer, create_message(MsgType.SPREAD_ASK_CONTENTS, {
            'files': files,
            'peer_addr': peer_addr[0],
            'peer_port': peer_addr[1],
            'origin': self.name
        }))

    def continue_content_recover(self, data_json):
        """spread of the content list from the system. Super peers pass the request to every SP in the token ring
        and, at the end, the initial Super Peer returns the contents to the peer who asked """
        contents = data_json['contents']
        if self.name == contents['origin']:
            # print(self.name, 'sending to peer')
            peer_addr = (contents['peer_addr'], contents['peer_port'])
            self.send_message(peer_addr,
                              create_message(MsgType.ANSWER_CONTENTS, contents['files']))
        else:
            files = [name for _, (_, _, name) in self.table.items()]
            contents['files'].extend(files)
            # print(self.name, contents['files'])
            self.send_message(self.next_peer, create_message(MsgType.SPREAD_ASK_CONTENTS, contents))

    def init_find_resource(self, peer_addr, data_json):
        """Peer asked this Super Peer to point him to the peer who has a given file in the system. Super peer will
        try to find it in its own table, if it is not, the super peer will pass the request to the token ring """
        file_name = data_json['contents']

        files = {name: (addr, port) for k, (addr, port, name) in self.table.items()}

        if file_name in files:
            self.send_message(peer_addr, create_message(MsgType.ANSWER_RESOURCE, {
                'address': peer_addr[0],
                'port': peer_addr[1],
                'file': file_name,
                'found': True,
                'location_ip': files[file_name][0],
                'location_port': files[file_name][1]
            }))
        else:
            self.send_message(self.next_peer, create_message(MsgType.SPREAD_FIND_RESOURCE, {
                'address': peer_addr[0],
                'port': peer_addr[1],
                'file': file_name,
                'origin': self.name,
                'found': False,
                'location_ip': None,
                'location_port': None
            }))

    def continue_find_resource(self, data_json):
        """The file request was spreaded to the token ring, every super peer will look for the file and, if it finds,
        will point to the peer who has the file """
        contents = data_json['contents']
        if self.name == contents['origin']:
            peer_addr = (contents['address'], contents['port'])
            self.send_message(peer_addr, create_message(MsgType.ANSWER_RESOURCE, contents))
        else:
            if contents['found']:
                self.send_message(self.next_peer, create_message(MsgType.SPREAD_FIND_RESOURCE, contents))
            else:
                files = {name: (addr, port) for k, (addr, port, name) in self.table.items()}

                if contents['file'] in files:
                    contents['found'] = True
                    file_data = files[contents['file']]
                    contents['location_ip'] = file_data[0]
                    contents['location_port'] = file_data[1]

                self.send_message(self.next_peer, create_message(MsgType.SPREAD_FIND_RESOURCE, contents))

    def clear_peer_list(self):
        """Checks if there are disconnected peers in the peer list and removes the inactive ones"""
        while True:
            peer_to_remove = list()
            for key in self.connected_peers:
                if time.time() - self.connected_peers[key] >= 10:
                    peer_to_remove.append(key)

            for key in peer_to_remove:
                del self.connected_peers[key]
                self.clear_peer_hashes(key)
                self.send_message(self.next_peer, create_message(MsgType.SPREAD_CLEAR, {
                    'address': key[0],
                    'port': key[1],
                    'origin': self.name
                }))
            time.sleep(1)

    def clear_peer_hashes(self, peer):
        """clear the hashes from disconnected peers"""
        print(self.name, '- Peer disconnected', peer)
        self.table = {k: v for k, v in self.table.items() if (v[0], v[1]) != peer}
        # print(self.name, 'tabela limpa ->', self.table)

    def print_table(self):
        while True:
            print(self.name, self.table)
            time.sleep(10)

    def send_message(self, addr, message):
        self.socket.sendto(message.encode(), addr)
