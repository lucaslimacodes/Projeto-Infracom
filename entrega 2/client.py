import socket as skt
import udp

#endereços do cliente e servidor
client_addr = ('localhost', 7070)
server_addr = ('localhost', 8080)
acknumber = 0
loss_probability = 0.1

file_path = 'teste.jpeg' # insira aqui o path do arquivo

#instanciando o cliente
client = udp.UDP(skt.AF_INET, skt.SOCK_DGRAM, client_addr, udp.MAX_BUFF_SIZE)

#Ação do Cliente - OBS.: Tenha certeza que o arquivo do servidor já esteja em execução

client.rdt_send(file_path, server_addr)


  