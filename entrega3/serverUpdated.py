import rdt_Entity
import threading
import time
import socket as skt
client_addr = ('127.0.0.1', 7070)
server_addr = ('127.0.0.1', 6060)

server_rdt = rdt_Entity.rdt_Entity(client_addr, server_addr)
transThread = threading.Thread(target=server_rdt.runTransmiter)
recThread = threading.Thread(target=server_rdt.runReceiver)

transThread.start()
recThread.start()
def Tx():
    while True:
        server_rdt.TxLock.acquire()
        while len(server_rdt.Tx) == 0:
            server_rdt.TxCondition.wait()
        server_rdt.socket.sendto(server_rdt.Tx[0], client_addr)
        server_rdt.Tx.pop(0)
        server_rdt.TxLock.release()

def Rx():
    while True:
        
        data, source = server_rdt.socket.recvfrom(1024)
        print("dado recebido: ", data)
        server_rdt.RxLock.acquire()
        server_rdt.Rx.append(data)
        server_rdt.RxCondition.notify_all()
        server_rdt.RxLock.release()

RxThread = threading.Thread(target=Rx)
TxThread = threading.Thread(target=Tx)
RxThread.start()
TxThread.start()
i = 0
while True:
    server_rdt.ReceiverBufferLock.acquire()
    while len(server_rdt.ReceiverBuffer) == 0:
        server_rdt.ReceiverBufferCondition.wait()
    print("cu:", server_rdt.ReceiverBuffer[0])
    server_rdt.ReceiverBuffer.pop(0)
    server_rdt.ReceiverBufferLock.release()
    if i >= 4:
        server_rdt.addMessageToTransmit("rolinhas")
        i=0
    i = i + 1
