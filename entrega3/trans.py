import rdt_transmiter
import rdt_receiver
import udp
import socket as skt


trans_addr = ('127.0.0.1', 7070)
rec_addr = ('127.0.0.1', 8080)

transmiter = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, trans_addr, udp.MAX_BUFF_SIZE, 1.0, rec_addr)

transmiter.setMessageFile('teste.jpeg')
transmiter.run()