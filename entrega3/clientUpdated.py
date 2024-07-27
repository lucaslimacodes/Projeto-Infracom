import rdt_Entity
import threading
import time

client_addr = ('127.0.0.1', 7070)
server_addr = ('127.0.0.1', 6060)

client_rdt = rdt_Entity.rdt_Entity(server_addr, client_addr)

transThread = threading.Thread(target=client_rdt.runTransmiter)
recThread = threading.Thread(target=client_rdt.runReceiver)

transThread.start()
recThread.start()

def Tx():
    while True:
        client_rdt.TxLock.acquire()
        while len(client_rdt.Tx) == 0:
            client_rdt.TxCondition.wait()
        print("dado enviado: ", client_rdt.Tx[0])
        client_rdt.socket.sendto(client_rdt.Tx[0], server_addr)
        client_rdt.Tx.pop(0)
        client_rdt.TxLock.release()

def Rx():
    while True:
        data, source = client_rdt.socket.recvfrom(1024)
        client_rdt.RxLock.acquire()
        client_rdt.Rx.append(data)
        client_rdt.RxCondition.notify()
        client_rdt.RxLock.release()

RxThread = threading.Thread(target=Rx)
TxThread = threading.Thread(target=Tx)
RxThread.start()
TxThread.start()

while True:
    client_rdt.ReceiverBufferLock.acquire()
    if len(client_rdt.ReceiverBuffer) > 0:
        print("jobas:",client_rdt.ReceiverBuffer[0])
        client_rdt.ReceiverBuffer.pop(0)
    client_rdt.ReceiverBufferLock.release()
    client_rdt.addMessageToTransmit("oRola")
    time.sleep(1)
    
