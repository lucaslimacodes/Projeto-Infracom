import socket as skt
import rdt_transmiter
import rdt_receiver
import time 
import json

server_addr = ('127.0.0.1', 8080)
server_socker = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
f = open('clientList.json')
dados = json.load(f)

clients = []
for i in dados:
    clients.append(i)
#clients.append('ricardo')
#clients.append('rodrigo')

connection = {}
for i in dados:
    connection[i] = False
#connection['ricardo'] = False
#connection['rodrigo'] = False

ports = {}
for i in dados:
    ports[i] = dados[i] 
#ports['ricardo'] = 3030
#ports['rodrigo'] = 4242

#lista de ids de acomodações que o cliente tem
acmList = {}
for i in dados:
    acmList[i] = []
#acmList['ricardo'] = []
#acmList['rodrigo'] = []

#informações de acomodação baseado no id
# (nome, local)
acmInfo = {}

#informações de reservas baseado no id
# (nomecliente, dia)
acmReservations = {}
idGen = 0

def getFreeDaysFromResv(id, returnString = True):
    days = [17,18,19,20,21,22]
    for (n,d) in acmReservations[id]:
        days.remove(d)
    if not returnString:
        return days
    saida = ""
    for day in days:
        saida = saida + str(day) + " "
    return saida

def isReservAllowed(clientName, resId, day):
    print("nome: ", clientName)
    print("id :", resId)
    print("dia: ", day)
    if resId in acmList[clientName]:
        print("f1")
        return False
    try:
        if day not in getFreeDaysFromResv(resId, returnString=False):
            print("f2")
            return False
    except:
        print("f3")
        return False
    
    return True

while True:
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024)
    rec.run()
    data = rec.receiveBuffer[0]
    origin = rec.transmiter

    if "LOGIN" in data.decode():
        name = data.decode().split(" ")[1]
        sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
        if name in clients and connection[name] == False: 
            sender.setMessageString("OK " + str(ports[name]))
            connection[name] = True
        else:
            sender.setMessageString("NOK")
        sender.run()
    elif "LOGOUT" in data.decode():
        name = data.decode().split(" ")[1]
        connection[name] = False
        sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
        sender.setMessageString("OK")
        sender.run()

    elif "CREATE" in data.decode():
        clientName = ""
        for client in clients:
            if ports[client] == origin[1]:
                clientName = client
        nome = data.decode().split(" ")[1]
        local = data.decode().split(" ")[2]
        repetido = False
        for client in clients:
            print("client atual: ",client)
            for i in acmList[client]:
                if acmInfo[i][0] == nome and acmInfo[i][1] == local:
                    repetido = True
                    break
        if repetido == False:
            print("nao repetifo")
            for client in clients:
                if ports[client] == origin[1]:
                    acmList[client].append(idGen)
                    acmInfo[idGen] = (nome, local)
                    acmReservations[idGen] = []
                    idGen = idGen + 1
                    sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
                    sender.setMessageString("OK")
                    sender.run()
                    break
            for client in clients:
                if client != clientName and connection[client]:
                    sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, ('127.0.0.1', ports[client] + 1))
                    sender.setMessageString(clientName + "/127.0.0.1:" + str(origin[1]) + " nova oferta criada// id: " + str(idGen-1) + " nome: " + nome + " local: " + local)
                    sender.run()
                
        else:
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
            sender.setMessageString("NOK")
            sender.run()
    elif data.decode() == "LIST:ACMD":
        saida = ""
        for client in clients:
            for id in acmList[client]:
                saida = saida + " id: " + str(id) + " nome: " +acmInfo[id][0] + " localização: " + acmInfo[id][1] + " dias: " +getFreeDaysFromResv(id) + " nome ofertante: " + client + '\n'
        sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
        sender.setMessageString(saida)
        sender.run()
    elif "BOOK" in data.decode():
        ident = data.decode().split(" ")[1]
        print("t1:", ident)
        dia = data.decode().split(" ")[2]
        print("d2:", dia)
        done = False
        clientName = ""
        for client in clients:
            if ports[client] == origin[1]:
                clientName = client
        if isReservAllowed(clientName, int(ident), int(dia)):
            done = True
            acmReservations[int(ident)].append((clientName, int(dia)))
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
            sender.setMessageString("OK")
        else:
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
            sender.setMessageString("NOK")
        sender.run()
        owner = ""
        if done:
            for client in clients:
                if int(ident) in acmList[client]:
                    owner = client
            ip = '127.0.0.1'
            print(owner)
            port = ports[owner] + 1
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, (ip,port))
            sender.setMessageString("[" + clientName +"/127.0.0.1:" + str(origin[1]) + "]" + " Reservou sua acomodação de id: " + ident + " nome: " + acmInfo[int(ident)][0] + " local: " + acmInfo[int(ident)][1] + " no dia: " + dia)
            sender.run()
    
    elif "CANCEL" in data.decode():
        ident = data.decode().split(" ")[1]
        print("t1:", ident)
        dia = data.decode().split(" ")[2]
        print("d2:", dia)
        done = False
        clientName = ""
        for client in clients:
            if ports[client] == origin[1]:
                clientName = client
        if (clientName, int(dia)) in acmReservations[int(ident)]:
            acmReservations[int(ident)].remove((clientName, int(dia)))
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
            done = True
            sender.setMessageString("OK")
        else:
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
            sender.setMessageString("NOK")
        sender.run()
        if done:
            owner = ""
            for client in clients:
                if int(ident) in acmList[client]:
                    owner = client
                    break
            ip = '127.0.0.1'
            port = ports[owner] + 1
            sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, (ip,port))
            sender.setMessageString("[" + clientName + "/127.0.0.1:" + str(ports[clientName]) + "]" + "(CANCELAMENTO) " + " id: " +ident + " nome: "+ acmInfo[int(ident)][0] + " local: " + acmInfo[int(ident)][1] + " no dia: "+dia)
            sender.run()

            for client in clients:
                if client == owner or connection[client] == False:
                    continue
                ip = '127.0.0.1'
                port = ports[client] + 1
                sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, (ip,port))
                sender.setMessageString("[" + owner + "/127.0.0.1:" + str(ports[owner]) + "]" + "uma nova disponibilidades para uma acomodação." + " nome: " + acmInfo[int(ident)][0] + " local: " + acmInfo[int(ident)][1] + " no dia: "+dia + " de id: " + ident)
                sender.run()                
    elif data.decode() == "LIST:MYACMD":
        clientName = ""
        for client in clients:
            if ports[client] == origin[1]:
                clientName = client
        saidaa = ""
        for id in acmList[clientName]:
            (n,l) = acmInfo[id]
            has = True
            saidaa = saidaa + " nome: " + n + " local: " + l + " dias disp: " + getFreeDaysFromResv(id)
            for (nc,diaa) in acmReservations[id]:
                saidaa = saidaa + "(" + nc +  ", " + origin[0] + ", " + str(origin[1]) + ", " + str(diaa) + ")"
            saidaa = saidaa + '\n'
        sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
        sender.setMessageString(saidaa)
        sender.run()
    elif data.decode() == "LIST:MYRSV":
        clientName = ""
        for client in clients:
            if ports[client] == origin[1]:
                clientName = client
        saida = ""
        for client in clients:
            if client == clientName:
                continue
            for id in acmList[client]:
                for (n,d) in acmReservations[id]:
                    if n == clientName:
                        saida = saida + "[" + client + "/" + '127.0.0.1' + ':' + str(ports[client]) + "]" + " nome: "+ acmInfo[id][0] + " local: " + acmInfo[id][1] + " dia: " + str(d) + '\n'
        sender = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, server_addr, 1024, 0.05, origin)
        sender.setMessageString(saida)
        sender.run()
        
