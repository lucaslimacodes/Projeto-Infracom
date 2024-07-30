import socket as skt
import rdt_transmiter
import rdt_receiver
import threading
import time
client_addr = ('127.0.0.1', 1234)
server_addr = ('127.0.0.1', 8080)
logged = False
currName = ""
def req_login(name : str):
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("LOGIN " + name)
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    print("nao rodou rec")
    rec.run()
    print("rodou rec")
    return rec.receiveBuffer[0].decode()

def req_logout():
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("LOGOUT " + currName)
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()

def req_create(n,l):
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("CREATE " + n + " " + l)
    print("rodou trans")
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()

def req_acmd():
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("LIST:ACMD")
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()

def req_book(id, dia):
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("BOOK " + id + " " + dia)
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()            

def req_cancel(id, dia):
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("CANCEL " + id + " " + dia)
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode() 

def req_myacmd():
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("LIST:MYACMD")
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()

def req_myrsv():
    trans = rdt_transmiter.RDT_transmiter(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024, 0.05, server_addr)
    trans.setMessageString("LIST:MYRSV")
    trans.run()
    rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, client_addr, 1024)
    rec.run()
    return rec.receiveBuffer[0].decode()    

mutex = threading.Lock()
def handle_broadcast():
    while True:
        mutex.acquire()
        if client_addr != ('127.0.0.1', 1234):
            
            
            ip = client_addr[0]
            port = client_addr[1] + 1
            rec = rdt_receiver.RDT_receiver(skt.AF_INET, skt.SOCK_DGRAM, (ip, port), 1024)
            mutex.release()
            rec.run()
            print(rec.receiveBuffer[0].decode())
            print("digite o comando: ")
        else:
            mutex.release()
thr = threading.Thread(target=handle_broadcast)
thr.start()
mutex.acquire()

while True:
    mutex.release()
    entrada = input("digite o comando: ")
    mutex.acquire()
    print("adquiriu o lock")
    if not logged:
        if "login" in entrada:
            nome = entrada.split(" ")[1]
            response = req_login(nome)
            code = response.split(" ")[0]
            if code == "OK":
                client_addr = ('127.0.0.1', int(response.split(" ")[1]))
                logged = True
                currName = nome
                print("login foi um sucesso")
            else:
                print("login falho")
        else:
            print("login ainda não realizado")
    else:
        if entrada == "logout":
            if req_logout() == "OK":
                currName = ""
                print("logout sucesso")
                logged = False
        elif "create" in entrada:
            n = entrada.split(" ")[1]
            l = entrada.split(" ")[2]
            if req_create(n,l) == "OK":
                print("criação foi um sucesso")
            else:
                print("criação falhou")
        elif entrada == "list:acmd":
            print(req_acmd())
        elif "book" in entrada:
            ident = entrada.split(" ")[1]
            dia = entrada.split(" ")[2]
            if req_book(ident, dia) == "OK":
                print("reserva realizada com sucesso")
            else:
                print("reserva falhou")
        elif "cancel" in entrada:
            ident = entrada.split(" ")[1]
            dia = entrada.split(" ")[2]
            if req_cancel(ident, dia) == "OK":
                print("cancelado com sucesso")
            else:
                print("erro ao cancelar")
        elif entrada == "list:myacmd":
            print(req_myacmd())
        elif entrada == "list:myrsv":
            print(req_myrsv())
        else:
            print("entrada invalida")
        