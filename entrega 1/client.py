import socket as skt
import udp

#endereços do cliente e servidor
client_addr = ('localhost', 7070)
server_addr = ('localhost', 8080)

file_path = 'teste.jpeg' # insira aqui o path do arquivo

#instanciando o cliente
client = udp.UDP(skt.AF_INET, skt.SOCK_DGRAM, client_addr, udp.MAX_BUFF_SIZE)

#Ação do Cliente - OBS.: Tenha certeza que o arquivo do servidor já esteja em execução

allChunks = udp.chunk_file(file_path, chunk_size=client.MAX_BUFF) #pega as chunks do arquivo de teste
for chunk in allChunks:
    client.send(server_addr, chunk) # envias as chunks ao servidor
    
client.send(server_addr, b"Done") #sinaliza ao servidor que todas as chunks foram enviadas

client.listen() #cliente espera a resposta do servidor com as chunks do mesmo arquivo

with open('clientReceivedFromServer', 'wb') as file: #criação de um arquivo para concatenar as chunks recebidas
    for chunk in client.dataBuffer:
        file.write(chunk)  