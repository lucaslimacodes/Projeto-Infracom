import rdt_transmiter
import rdt_receiver
import udp
import socket as skt

trans_addr = ('127.0.0.1', 7070)
rec_addr = ('127.0.0.1', 8080)

receiver = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, rec_addr, udp.MAX_BUFF_SIZE, trans_addr)

receiver.run()

with open('serverReceivedFromClient', 'wb') as file:
    for chunk in receiver.receiveBuffer:
        file.write(chunk)  #concatena as chunks num único arquivo