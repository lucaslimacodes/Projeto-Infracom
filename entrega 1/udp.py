import socket as skt
import time

class UDP():
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF):
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.bind(sckt_binding)
        self.sckt.settimeout(0.1)
        self.dataBuffer = [] #conterá os chunks do arquivo separado em pacotes de 1024 bytes

        if self.sckt is None:
            raise Exception("Socket not available.")
        
        self.MAX_BUFF = MAX_BUFF

    def listen(self):
        while True:
            try:
                data, origin = self.sckt.recvfrom(self.MAX_BUFF)
        
                if data == b"Done": #se o cliente receber Done de um servidor ou vice-versa, o listen parará
                    break
                self.dataBuffer.append(data) # concatenando o dado recebido para o buffer
            except skt.timeout:
                continue
        
    def send(self, server_addr: tuple[str, int], msg: bytes):
        self.sckt.sendto(msg, server_addr)
        time.sleep(0.0001)



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