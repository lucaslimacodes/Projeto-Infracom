import socket as skt
import udp

#set do endereço e porta do cliente e servidor
client_addr = ('localhost', 7070)
server_addr = ('localhost', 8080)

server = udp.UDP(skt.AF_INET, skt.SOCK_DGRAM, server_addr, udp.MAX_BUFF_SIZE)


#Ação do servidor - OBS.: Inicie o servidor antes do cliente


server.listen() #escuta o cliente até receber todas as chunks
with open('serverReceivedFromClient', 'wb') as file:
    for chunk in server.dataBuffer:
        file.write(chunk)  #concatena as chunks num único arquivo
        server.send(client_addr, chunk) # reenvia as chunks de volta ao cliente
    
server.send(client_addr, b"Done") # avisa ao cliente que todas as chunks já foram enviadas