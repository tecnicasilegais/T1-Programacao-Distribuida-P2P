import os
import random
import string
import superpeer


class Peer(superpeer.SuperPeer):

    def __init__(self,name, addr, port, next_peer):
        super().__init__(name, addr, port, next_peer)
        self.create_folder_and_file()

    def create_folder_and_file(self):
        self.create_folder()
        self.create_random_files()
    
    def create_folder(self):
        if not os.path.exists('file/'+self.name):
            os.makedirs('file/'+self.name)


    def create_random_files(self):
        for i in range(2):
            file = open('file/'+self.name + "/"+ self.generate_random_text(4) + '-' + self.name+ ".txt", "w")
            file.write(self.generate_random_text())
            file.close()

    def generate_random_text(self, size=100):
        size = random.randint(1, size)
        return ''.join(random.choice(string.ascii_letters) for _ in range(size))