import socket
import threading
import time
import random
from time import sleep
import json
import psycopg2


#les sleeps sont utilisé pour eviter le plus possible la congestion des messages dans le buffer

#Initialiser les variables 
list_clients = dict()
list_threads = []
leader = None
archive = dict()

#Connection au serveur 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("192.168.137.1", 85))
#Vider la base de donnees
connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="projet_comm")
cursor = connection.cursor()
cursor.execute("delete from temperatures")
connection.commit()
cursor.close()
connection.close()

#Fonction qui ecrit les donnees dans la BD
def write_bd(new_data, filename='log.json'):
    #Write to the database
    connection = psycopg2.connect(user="postgres",
                                password="admin",
                                host="127.0.0.1",
                                port="5432",
                                database="projet_comm")
    cursor = connection.cursor()
    cursor.execute("insert into temperatures values (%s,%s,now())",(new_data[0],new_data[1]))
    connection.commit()
    cursor.close()
    connection.close()

#Thread pour la reception des messages des diffents capteurs
def receive_thread(sock):
    global archive
    global list_clients
    spam= sock[0].recv(1024).decode()
    while True:
        sleep(random.uniform(0.1, 1))
        message = sock[0].recv(1024).decode()
        archive[sock[1][1]].append(message)
        #Si le message commence avec Alert on l'affiche 
        if message.startswith("Alert"):
            print("j'ai une aletre " + message)
            message = message.split("/")
            try:
                list_clients[ int(message[1][:5])].send(b"alert")    
                time.sleep(5)
            except: 
                pass
        else :
            try:
              
                sleep(random.uniform(0.1, 1))
                rapport = str(sock[1][1]) + "/" + str(message[:2])
                write_bd((str(sock[1][1]), str(message[:2])))
                print(rapport)
                list_clients[leader].send(rapport.encode())
            except: 
                pass
              
#Fonction qui réalise lelection
def election():
    global list_clients
    global list_threadsi
    global leader
    
    #Ecouter touts les appareils pendant 20 secondes
    sock.listen()
    sock.settimeout(20)
    start_time = time.time()
    seconds = 10
    while True:
        try:
            #Accepter les connexion et enregistrer le client dans liste_clients
            (conn_sock, client_info) = sock.accept()
            print(client_info[1])
            archive.setdefault(client_info[1], list())
            list_clients[client_info[1]] = conn_sock
            list_threads.append(threading.Thread(target=receive_thread, args=((conn_sock, client_info),)))
        except Exception as e:
            print(e)
            pass
            
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > seconds:
            break
    all_ids = [i for i in list_clients.keys()]
    leader = max(all_ids)
    all_ids = "/".join([str(i) for i in all_ids])
    # Envoyer les id a tout le monde pour pouvoir faire l'election
    for b in list_clients.keys():
        list_clients[b].send(all_ids.encode())

    return leader

#Fonction globale qui lance lelection et les threads 
def server():
    global leader
    # Phase d'election
    leader = election()

    for client in list_threads:
        client.start()


server()

"""
Old version of the code
import socket
import threading
import time
import random
from time import sleep
import json
import psycopg2


list_clients = dict()
list_threads = []
leader = None
archive = dict()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("192.168.137.1", 85))


# Duplicata du code plus bas
'''
def send_thread(sock, list_client):
    message = sock.recv(1024).decode()
    print(message)
    for client in list_client:
        time.sleep(random.randint(0, 2))
        client[0].send(message.encode())
        print("i sent to" + str(client[1]))
'''

def write_json(new_data, filename='log.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data[new_data[0]].append(new_data[1])
        json.dump(file_data, file, indent = 2)
        #Write to the database
        connection = psycopg2.connect(user="postgres",
                                  password="admin",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="projet_comm")
cursor = connection.cursor()
cursor.execute("delete from temperatures")
connection.commit()
cursor.close()
connection.close()


def write_json(new_data, filename='log.json'):
    #Write to the database
    connection = psycopg2.connect(user="postgres",
                                password="admin",
                                host="127.0.0.1",
                                port="5432",
                                database="projet_comm")
    cursor = connection.cursor()
    cursor.execute("insert into temperatures values (%s,%s,now())",(new_data[0],new_data[1]))
    connection.commit()
    cursor.close()
    connection.close()

def receive_thread(sock):
    global archive
    global list_clients
    spam= sock[0].recv(1024).decode()
    while True:
        sleep(random.uniform(0.1, 1))
        message = sock[0].recv(1024).decode()
        archive[sock[1][1]].append(message)
        if message.startswith("Alert"):
            print("j'ai une aletre " + message)
            message = message.split("/")
            try:
                list_clients[ int(message[1][:5])].send(b"alert")    
                time.sleep(5)
            except: 
                pass
        else :
            #print(archive.values())
            try:
                sleep(random.uniform(0.1, 1))
                rapport = str(sock[1][1]) + "/" + str(message[:2])
                write_json((str(sock[1][1]), str(message[:2])))
                print(rapport)
                list_clients[leader].send(rapport.encode())
            except: 
                pass

def election():
    global list_clients
    global list_threadsi
    global leader
    sock.listen()
    sock.settimeout(20)
    start_time = time.time()
    seconds = 10
    while True:
        try:
            (conn_sock, client_info) = sock.accept()
            print(client_info[1])
            archive.setdefault(client_info[1], list())
            list_clients[client_info[1]] = conn_sock
            list_threads.append(threading.Thread(target=receive_thread, args=((conn_sock, client_info),)))
        except Exception as e:
            print(e)
            pass
            
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > seconds:
            break
    all_ids = [i for i in list_clients.keys()]
    leader = max(all_ids)
    all_ids = "/".join([str(i) for i in all_ids])
    # Envoyer les id a tout le monde
    for b in list_clients.keys():
        list_clients[b].send(all_ids.encode())

    return leader


def server():
    global leader
    # Phase d'election
    leader = election()

    for client in list_threads:
        client.start()


server()
"""
