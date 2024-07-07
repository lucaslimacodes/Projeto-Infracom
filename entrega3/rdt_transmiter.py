import socket as skt
import time
import udp

#Definindo os estados
SEND_PKT_0 = 0
WAIT_ACK_0 = 1
SEND_PKT_1 = 2
WAIT_ACK_1 = 3


class RDT_transmiter(udp.UDP):
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF, timeout, receiver_addr):
        super().__init__(sckt_family, sckt_type, sckt_binding, MAX_BUFF)
        self.sckt.settimeout(timeout)
        self.receiver = receiver_addr
        self.state = SEND_PKT_0
        self.timeoutFlag = False
        self.sendBuffer = []
        self.sendBufferConfigured = False

    def listenOne(self):
        while True:
            try:
                data, origin = self.sckt.recvfrom(self.MAX_BUFF)
        
                if origin == self.receiver: 
                    return data
                    
                 
            except skt.timeout:
                self.timeoutFlag = True
                return -1
    
    def setMessageString(self, message : str):
        messageByte = message.encode()
        if(len(message) <= 1023):
            self.sendBuffer[0] = bytes([0]) + messageByte
        else:
            chunks = []
            for i in range(0, len(messageByte), 1023):
                chunks.append(messageByte[i:i + 1023])
            
            for i in range(0, len(chunks)):
                self.sendBuffer.append(bytes([i%2]) + chunks[i])

        self.sendBufferConfigured = True


    def setMessageFile(self, file_path):
        allChunks = udp.chunk_file(file_path, 1023)
        for i in range(0, len(allChunks)):
            self.sendBuffer.append(bytes([i%2]) + allChunks[i])
        self.sendBufferConfigured = True

    def run(self):
        if(self.sendBufferConfigured == False):
            raise Exception("Buffer de envio não foi propriamente configurado")
        
        while(len(self.sendBuffer) > 0):
            if(self.state == SEND_PKT_0):
                self.send(self.receiver, self.sendBuffer[0])
                print("enviou pacote 0")
                self.state = WAIT_ACK_0
            elif(self.state == WAIT_ACK_0):
                data = self.listenOne()
                if(self.timeoutFlag == True):
                    print("TIMEOUT, reenviando pacote")
                    self.send(self.receiver, self.sendBuffer[0]) #timeout, reenviando o pacote
                    self.timeoutFlag = False
                elif(data == bytes([1])):
                    print("ack errado, não farei nada")
                    a=a # fazer nada com ack errado
                else:
                    print("Ack recebido com sucesso")
                    self.sendBuffer.pop(0)
                    self.state = SEND_PKT_1
            elif(self.state == SEND_PKT_1):
                print("enviou pacote 1")
                self.send(self.receiver, self.sendBuffer[0])
                self.state = WAIT_ACK_1
            elif(self.state == WAIT_ACK_1):
                data = self.listenOne()
                if(self.timeoutFlag == True):
                    print("TIMEOUT, reenviando pacote")
                    self.send(self.receiver, self.sendBuffer[0]) #timeout, reenviando o pacote
                    self.timeoutFlag = False
                elif(data == bytes([0])):
                    print("ack errado, não farei nada")
                    a=a # fazer nada com ack errado
                else:
                    print("Ack recebido com sucesso")
                    self.sendBuffer.pop(0)
                    self.state = SEND_PKT_0

        self.send(self.receiver, b"Done")



                

    
