import socket as skt
import threading
NONE = -1
RECEIVER = 0
TRANSMITER = 1

SEND_PKT_0 = 0
WAIT_ACK_0 = 1
SEND_PKT_1 = 2
WAIT_ACK_1 = 3

WAIT_PKT_0 = 0
WAIT_PKT_1 = 1

class rdt_Entity():
    def __init__(self, pier_addr, my_addr):
        self.state = NONE
        self.stateLock = threading.Lock()
        self.stateCondition = threading.Condition(lock=self.stateLock)

        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind(my_addr)

        self.transmiterBuffer = []
        self.transmiterBufferLock = threading.Lock()
        self.transmiterBufferCondition = threading.Condition(lock=self.transmiterBufferLock)

        self.ReceiverBuffer = []
        self.ReceiverBufferLock = threading.Lock()
        self.ReceiverBufferCondition = threading.Condition(lock=self.ReceiverBufferLock)


        self.Tx = []
        self.TxLock = threading.Lock()
        self.TxCondition = threading.Condition(self.TxLock)
    
        self.Rx = []
        self.RxLock = threading.Lock()
        self.RxCondition = threading.Condition(self.RxLock)

        self.pier = pier_addr

        self.transmiterState = SEND_PKT_0
        self.receiverState = WAIT_PKT_0

        self.wakeCondition = threading.Condition()


    def addMessageToTransmit(self, message : str):
        print("tentando adquirir")
        self.transmiterBufferLock.acquire()
        print("ad")
        self.transmiterBuffer.append(message.encode())
        self.transmiterBufferCondition.notify()
        self.transmiterBufferLock.release()
    
    def getLastDataReceived(self):
        self.ReceiverBufferLock.acquire()
        while(len(self.ReceiverBuffer) == 0):
            self.ReceiverBufferCondition.wait()
        data = self.ReceiverBuffer[0]
        self.ReceiverBuffer.pop(0)
        self.ReceiverBufferLock.release()
        return data

    def isRxNotEmpty(self):
        return (len(self.Rx)!= 0)
    
    def runTransmiter(self):
        while True: 
            

            self.transmiterBufferLock.acquire()
            while(len(self.transmiterBuffer) == 0):
                print("esperando")
                self.transmiterBufferCondition.wait()
                print("saiu")
            
            self.stateLock.acquire()
            while self.state == RECEIVER:
                self.stateCondition.wait()
            self.state = TRANSMITER
            print(self.transmiterState)
            if self.transmiterState == SEND_PKT_0:
                self.TxLock.acquire()
                print("trasmissor enviou pacote pro tx")
                self.Tx.append(bytes([0]) + self.transmiterBuffer[0])
                self.TxCondition.notify()
                self.TxLock.release()
                self.transmiterState = WAIT_ACK_0
            elif self.transmiterState == WAIT_ACK_0:
                self.RxLock.acquire()
                print("esperando timer")
                wasTout = True
                if len(self.Rx) == 0:
                    wasTout = self.RxCondition.wait(timeout=1.0)
                print("saiu da espera")
                if wasTout == False:
                    print("timeout")
                    self.transmiterState = SEND_PKT_0
                else:
                    print("não foi timeout pois")
                    print("transmiter poa: ", self.Rx)
                    if self.Rx[0] == bytes([0]):
                        print("ack recebido")
                        self.transmiterState = SEND_PKT_1
                        self.transmiterBuffer.pop(0)
                        self.state = NONE
                        self.stateCondition.notify()
                    else:
                        print("wrong ack")
                    
                    self.Rx.pop(0)
                self.RxLock.release()
            elif self.transmiterState == SEND_PKT_1:
                self.TxLock.acquire()
                print("trasmissor enviou pacote pro tx")
                self.Tx.append(bytes([1]) + self.transmiterBuffer[0])
                self.TxCondition.notify()
                self.TxLock.release()
                self.transmiterState = WAIT_ACK_1
            elif self.transmiterState == WAIT_ACK_1:
                self.RxLock.acquire()
                wasTout = True
                if len(self.Rx) == 0:
                    wasTout = self.RxCondition.wait(timeout=1.0)
                if wasTout == False:
                    print("timeout")
                    self.transmiterState = SEND_PKT_1
                else:
                    print("não foi timeout pois")
                    print("transmiter poa: ", self.Rx)
                    if self.Rx[0] == bytes([1]):
                        print("ack recebido")
                        self.transmiterState = SEND_PKT_0
                        self.transmiterBuffer.pop(0)
                        self.state = NONE
                        self.stateCondition.notify()
                    else:
                        print("wrong ack")
                    
                    self.Rx.pop(0)
                self.RxLock.release()

            self.stateLock.release()
            self.transmiterBufferLock.release()
        
        
        #lembrar de dar unlock nos dois lock acima

    def runReceiver(self):
        while True:
            self.RxLock.acquire()
            while(len(self.Rx) == 0 or self.Rx[0] == bytes([0]) or self.Rx[0] == bytes([1])):
                #a = len(self.Rx) == 0
                #b = -1
                #c = -1
                #if len(self.Rx) != 0:
                    #b = self.Rx[0] == bytes([0])
                    #c = self.Rx[0] == bytes([1])
                
                #print(a,b,c)
                #print(self.Rx)
                print("receiver dormindo no rx")
                print(self.Rx)
                self.RxCondition.wait()
            print("receiver acordou no rx")
            self.stateLock.acquire()
            while self.state == TRANSMITER:
                print("receiver dormiu no condition")
                self.stateCondition.wait()
            print("receiver acordou no condition")
            print(self.Rx)
            self.state = RECEIVER
            if self.receiverState == WAIT_PKT_0:
                if self.Rx[0][0] == bytes([1]):
                    self.TxLock.acquire()
                    self.Tx.append(bytes[1])
                    self.TxCondition.notify()
                    self.TxLock.release()
                else:
                    self.TxLock.acquire()
                    print("ack enviado")
                    self.Tx.append(bytes([0]))
                    self.TxCondition.notify()
                    self.TxLock.release()
                    self.ReceiverBufferLock.acquire()
                    self.ReceiverBuffer.append(self.Rx[0][1:])
                    print("receba:" ,self.ReceiverBuffer)
                    self.ReceiverBufferCondition.notify()
                    self.ReceiverBufferLock.release()
                    self.receiverState = WAIT_PKT_1
                    self.state = NONE
                    self.stateCondition.notify()

                self.Rx.pop(0)
            elif self.receiverState == WAIT_PKT_1:
                if self.Rx[0][0] == bytes([0]):
                    self.TxLock.acquire()
                    self.Tx.append(bytes([0]))
                    self.TxCondition.notify()
                    self.TxLock.release()
                else:
                    self.TxLock.acquire()
                    print("ack enviado")
                    self.Tx.append(bytes([1]))
                    self.TxCondition.notify()
                    self.TxLock.release()
                    self.ReceiverBufferLock.acquire()
                    self.ReceiverBuffer.append(self.Rx[0][1:])
                    print("receba", self.ReceiverBuffer)
                    self.ReceiverBufferCondition.notify()
                    self.ReceiverBufferLock.release()
                    self.receiverState = WAIT_PKT_0
                    self.state = NONE
                    self.stateCondition.notify()

                self.Rx.pop(0)

            self.stateLock.release()
            self.RxLock.release()


            



        
        

        

            

            