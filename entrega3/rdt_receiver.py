import socket as skt
import time
import udp

WAIT_PKT_0 = 0
WAIT_PKT_1 = 1

class RDT_receiver(udp.UDP):
    def __init__(self, sckt_family, sckt_type, sckt_binding, MAX_BUFF, transmiter):
        super().__init__(sckt_family, sckt_type, sckt_binding, MAX_BUFF)
        self.transmiter = transmiter
        self.receiveBuffer = []
        self.state = WAIT_PKT_0

    def listenOne(self):
        while True:
            data, origin = self.sckt.recvfrom(self.MAX_BUFF)
            if origin == self.transmiter: 
                return data
            
    def run(self):
        while True:
            if(self.state == WAIT_PKT_0):
                data = self.listenOne()
                if(data == b"Done"):
                    break
                if(data[0] == bytes([1])):
                    self.send(self.transmiter, bytes([1]))
                else:
                    self.receiveBuffer.append(data[1:])
                    self.send(self.transmiter, bytes([0]))
                    self.state = WAIT_PKT_1
            elif(self.state == WAIT_PKT_1):
                data = self.listenOne()
                if(data == b"Done"):
                    break
                if(data[0] == bytes([0])):
                    self.send(self.transmiter, bytes([0]))
                else:
                    self.receiveBuffer.append(data[1:])
                    self.send(self.transmiter, bytes([1]))
                    self.state = WAIT_PKT_0          

                    
                 
