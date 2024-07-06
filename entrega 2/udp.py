import socket as skt
import time
import random

class UDP():
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF):
        self.sckt = skt.socket(sckt_family, sckt_type)
        self.sckt.bind(sckt_binding)
        self.sckt.settimeout(1.0)
        self.dataBuffer = [] #conterá os chunks do arquivo separado em pacotes de 1024 bytes
        self.expectednumber = 0
        self.lossprobability = 0.1
        self.acknumber = 0

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
    
    def rdt_listen(self):
        while True:
            try:
                data, origin = self.sckt.recvfrom(self.MAX_BUFF)

                if data == b"Done":
                    break
                
                # Extrai o número de sequência (primeiro byte)
                seqreceived = data[0:1]
                seqreceived = int.from_bytes(seqreceived, 'big')
                print("chunck de numero de sequencia ", seqreceived)



             # Extrai os dados do chunk (restante dos bytes)
                data = data[1:]
                if seqreceived == self.expectednumber:
                    ack = seqreceived.to_bytes(1, 'big')
                    print("Enviando ACK ", seqreceived)
                    if not(random.random() < self.lossprobability): #Chance de não enviar o ACK
                        self.sckt.sendto(ack, origin)
                    else:
                        print("ACK perdido")
                    self.dataBuffer.append(data)
                
                    # Alterna o número de sequência esperado
                    self.expectednumber = 1 - self.expectednumber
                else:
                    # Reenvia o ACK do último número de sequência esperado
                    ack = (1 - self.expectednumber).to_bytes(1, 'big')
                    if not(random.random() < self.lossprobability): 
                        self.sckt.sendto(ack, origin)
                    else:
                        print("ACK perdido")
            except skt.timeout:
                continue
            


        
    def send(self, server_addr: tuple[str, int], msg: bytes):
        self.sckt.sendto(msg, server_addr)
        time.sleep(0.0001)

    def rdt_send(self, file_path, server_addr):
        allChunks = chunk_file(file_path, chunk_size=(self.MAX_BUFF)-1) #pega as chunks do arquivo de teste
        for chunk in allChunks:
            chunk_with_ack = self.acknumber.to_bytes(1, 'big') + chunk  # Concatena o número de sequência ao chunk
            if not(random.random() < self.lossprobability): # Chances de não enviar o pacote
                self.send(server_addr, chunk_with_ack)
                print("Chunck enviado: ", self.acknumber)
            else:
                print("Chunck perdido")
            while True:
                try:
                    data, origin = self.sckt.recvfrom(1)
                    data = int.from_bytes(data, 'big')
                    print("ACK Received: ", data)
                    if data == self.acknumber:
                        self.acknumber = 1 - self.acknumber  # Alterna entre 0 e 1
                        break
                    else:
                        if not(random.random() < self.lossprobability):
                            self.send(server_addr, chunk_with_ack) #Caso receba dois ACKs iguais(pacotes duplicados)
                            print("Resending...")
                        else:
                            print("Chunck perdido")
                except skt.timeout: #Timeout: demora para receber o pacote de confirmação
                    if not(random.random() < self.lossprobability):
                        self.send(server_addr, chunk_with_ack)
                        print("Resending..., timeout")
                    else:
                        print("Chunck perdido")
        self.send(server_addr, b"Done")



def chunk_file(file_path, chunk_size=1023): # função que divide um arquivo em chunks de 1024 bytes
    chunks = []
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks

MAX_BUFF_SIZE = 1024