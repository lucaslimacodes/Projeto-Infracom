import socket as skt
import time

class UDP():
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF):
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.setsockopt(skt.SOL_SOCKET, skt.SO_REUSEADDR, 1)
        self.sckt.bind(sckt_binding)

        if self.sckt is None:
            raise Exception("Socket not available.")
        
        self.MAX_BUFF = MAX_BUFF

    def send(self, server_addr: tuple[str, int], msg: bytes):
        self.sckt.sendto(msg, server_addr)
        time.sleep(0.0001)
    
    def listenOne(self):
        return self.sckt.recvfrom(self.MAX_BUFF)
        



def chunk_file(file_path, chunk_size=1024): # função que divide um arquivo em chunks de 1024 bytes
    chunks = []
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks

MAX_BUFF_SIZE = 1024