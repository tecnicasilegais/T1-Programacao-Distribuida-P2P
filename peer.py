import os
import random
import socket
import string
import hashlib


def generate_random_text(size=100):
    size = random.randint(1, size)
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))


def file_to_hash(file):
    return hashlib.sha256(file.encode()).hexdigest() # usar outra coisa que gere um hash mais simples 


class Peer:

    def __init__(self, name, addr, port,  random_sp=''):
        self.addr = addr
        self.name = name
        self.port = port
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((addr, port))
        self.random_sp = random_sp
        self.create_folder_and_file()
        self.read_files()

    def create_folder_and_file(self):
        self.create_folder()
        self.create_random_files()

    def create_folder(self):
        if not os.path.exists('file/' + self.name):
            os.makedirs('file/' + self.name)

    def create_random_files(self):
        for i in range(2):
            file = open('file/' + self.name + "/" + generate_random_text(4) + '-' + self.name + ".txt", "w")
            file.write(generate_random_text())
            file.close()

    def read_files(self):
        for file in os.listdir('file/' + self.name):
            self.send_hash(file)

    def send_hash(self, file):
        self.send_message(self.random_sp, file_to_hash(file))

    def send_message(self, addr, message):
        self.socket.sendto(message.encode(), addr) 
