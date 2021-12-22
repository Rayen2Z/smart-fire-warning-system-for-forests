# préparation des librairies qui vont être utilisées
import socket
import random
import time
import threading
import platform

# Création de la socket du capteur avec la méthode socket de la librairie socket 
csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# initialisation de la température du capteur (temperature ambiante)
temp = 25

# Définition du seuil de température qui déclenche une alerte 
threshold = 27

myself = 0
status = 0
sensor = None

""" vérifier si le capteur est un raspberry , pour qu'il puisse génerer les températures à partir de son sense heat , sinon (si c'est un pc) : 
les températures sont générées par une fonction aléatoire """
if platform.system() == "Linux":
    from sense_hat import SenseHat
    sensor = SenseHat()
    


# Définition d'une fonction qui reçoit les données du serveur , EXÉCUTÉE SEULEMENT EN CAS OU LE CAPTEUR EST LE LEADER 
def receive_data():
    
    global threshold  
    global csock
    global status
    while True:  # tant que le capteur est vivant (connecté)
        
        # bloc Try except pour gérer les exceptions des pertes de connexions avec le serveur 
        try:
            
            message = csock.recv(1024).decode()  # le message reçu est stocké dans une variable en utilisant la fonction socket.recv() 
            message = message.split("/")      # le message est découpé en deux , car le serveur a envoyé : num_socket/temperature 
            print(message)      # afficher l'id de la station avec sa température 
            
            
            if message[0] == "alert": 
               
                alert()
            else:
                if (int(message[1][:2]) > threshold):
                    a = "Alert/" + str(message[0])
                    csock.sendall(a.encode())
                    time.sleep(random.uniform(0.1, 0.5))
                    
                    
        except (ConnectionResetError, OSError):  # gestion de l'exception d'une possible déconnexion du serveur 
            
           
            # le sleep suivant est nécessaire pour forcer un controle aux temps différents entre les 2 threads send et receive
            time.sleep(random.uniform(0.1, 0.5))
            
            if (status != -1 ):  #  si le thread n'est pas entrain de se reconnecter 
                #print("receive thread trying")
                status = -1
                while(status == -1):   # essai de reconnexion 
                    csock.close()      # fermer l'ancienne socket 
                    csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # création d'une nouvelle socket 
                    csock.settimeout(10)         # mettre un timeout de 10 secondes pour éviter une reconnexion des deux parties send et receive 
                    
                    
                    try:   # block try except pour gérer la reconnexion
                        csock.connect(("192.168.137.1", 85))
                        status = 1
                        time.sleep(random.uniform(8, 10))
                        break
                        
                    except:
                        # l'exception qui occure ici est celle du time out du connect on veut pas que le thread
                        # crash et arréte l execution
                        print("reconnecting")
                        pass
                    
            else:  # si statu=-1 (essaie de se reconnecter) , alors attend 5 secondes 
                #print("Already reconnecting...")
                time.sleep(5)

                
def sense():   # fonction qui affiche les températures si le capteur est un raspberry 
    try:
        sensor.clear()
        return round(sensor.get_temperature())
    except:
        return 0
    
    

def alert():     
    if sensor != None:    # sensor different de None c'est à dire que c'est un raspberry
        sensor.clear()
        sensor.show_message("Alert !", text_colour = (255, 0, 0))  # afficher une alerte sur le raspberry 
    else:
        print("Alert !")  # dans le cas d'un pc et non raspberry , afficher un message d'alerte 
        time.sleep(5)
        


def alert_thread():   # fonction pour lancer une alerte dans le cas ou c'est pas le leader 
    global csock
    global status
    while True:
        try:
            # l'exception est là
            message = csock.recv(1024).decode()
            if message.startswith("alert"):
                alert()
        except (ConnectionResetError, OSError):
            time.sleep(5)  
            


def send_data():   # fonction éxécutée par leader ou pas , pour envoyer des températures 
    global temp
    global status
    global csock
    while True:
        # si raspberry : envoie temp de la fonction sense() , sinon genere des temperatures aléatoires avec randint()
        temp = (temp + random.randint(0, 2))*(sensor == None) + sense()*(sensor != None) 
        try:
            time.sleep(random.uniform(0.1, 0.5))   # temps d'attente entre chaque envoi 
            csock.sendall(str(temp).encode())    # envoi avec la fonction socket.sendall()
            print("ma temperature" + str(temp))   # afficher ma température 
        
        # gestion des exceptions de déconnexions du serveur 
        except (ConnectionResetError, OSError, BrokenPipeError) as e:
            print(e)
            
            # le sleep suivant est nécessaire pour forcer un controle aux temps différents entre les 2 threads send et receive
            time.sleep(random.uniform(0, 0.5))
            
            if (status != -1 ):  # si n'essaie pas de se reconnecter 
                print("send data trying")
                status = -1         
                while(status == -1):   # statut=-1 : qui veut dire essaie de se reconnecter 
                    csock.close()       # fermer la socket précedente
                    csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # créer une nouvelle socket 
                    csock.settimeout(10)             # timeout pour eviter des reconnexions en meme temps 
                    
                    try:
                        csock.connect(("192.168.137.1", 85))    # reconnexion 
                        status = 1  # statut = 1 qui veut dire connecté . 
                        break
                    except:
                        # l'exception qui occure ici est celle du time out du connect on veut pas que le thread
                        # crash et arréte l execution
                        print("Reconnecting...")
                        pass
            else:
                print("Receiving thread already reconnecting")
                pass
        time.sleep(random.uniform(8, 10))

def reElection():
    global myself
    global csock
    myself = csock.getsockname()

   

def capteur():   # fonction capteur qui est executé dans toutes les stations 
    global myself
    global status
    global csock
    
    while True:  
        try:
            csock.connect(("192.168.137.1", 85))    # connexion au serveur 
            status = 1               # statut =1 : connecté 
            break
        except:
            pass
    myself = csock.getsockname()      # récuperation de mon id 
    msg = str(myself[1])             # le mettre dans une variable 
    csock.sendall(msg.encode())        # envoyer mon id au serveur 
    while True:
        try:
            datafromserver = csock.recv(1024)      
            all_sockets = datafromserver.decode().split("/")
            break
        except:
            pass
    id_leader = max([int(e) for e in all_sockets])    # éléction du leader (id le plus grand )
    
    
    
    if id_leader == myself[1]:          # si je suis le leader :           
        print("Je suis le leader")
        
        # je crée un Thread d'écoute qui sert à recevoir les messages du serveur 
        listening_thread = threading.Thread(target = receive_data)   
        listening_thread.start()
        
        # je crée un Thread d'envoi 
        sending_thread = threading.Thread(target = send_data)
        sending_thread.start()
        
        
    else:   # si je ne suis pas leader
        
        
        print("Je suis pas un leader")
        
        # je crée un thread d'envoi
        sending_thread = threading.Thread(target = send_data)
        sending_thread.start()
        
        
        # je crée un thread pour lancer des alertes 
        alarm_thread = threading.Thread(target = alert_thread)
        alarm_thread.start()



capteur()
