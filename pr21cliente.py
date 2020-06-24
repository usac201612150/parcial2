"""                                                                        #DRRP
Este codigo debe ser ejecutado en una carpeta en la que existan los siguientes archivos:
    -usuario (Dentro de el, ingresar 201603188 o 201612150)
    -salas   (Dentro de el, ingresar salas validas Ej: 21S01)
"""
########################################################################## 
####################        LIBRERIAS               ###################### 
########################################################################## 
import paho.mqtt.client as mqtt          
import logging                          
import time
import os
import threading
import sys
import socket
##########################################################################
####################         DEFINICIONES           ######################
########################################################################## #DRRP
grupo=21
MQTT_HOST = "167.71.243.238" #Necesarios para MQTT
MQTT_PORT = 1883
MQTT_USER = "proyectos"
MQTT_PASS = "proyectos980"
qos = 2
USUARIOS="usuarios"#Definicion para archivos
SALAS="salas"
AUDIO="audio"
##########################################################################
####################        METODOS & Clases       #######################
##########################################################################
class Instructions(object):                                                #DRRP Clase para el manejo de las instruciones
    def __init__(self, comando):
        self.comando=comando

    def inicial(self):                                                     #DRRP Despliega el menu grafico
        print("para su uso favor ingresar a una de las siguientes ramas")
        print("\t1. Enviar texto \n\t\ta.Enviar mensaje directo\n\t\tb.Enviar a una sala")
        print("\t2. Enviar nota de voz")
        print("\t3. Reproducir ultimo audio recivido")
        print("\t4. Mostrar opciones")
        print("\t5. Desconectarme")

    def direct(self):                                                       #DRRP Instruccion para enviar mensajes directos
        Destinatario=input("Destinatario:")
        texto_enviar=input("Que le quieres decir a "+Destinatario+": ")     
        return Destinatario, texto_enviar

    def grupo(self):                                                         #DRRP Instruccion para enviar mensajes a salas
        Destinatario=input("Sala elegida:")
        texto_enviar=input("Que le quieres decir a la sala "+Destinatario+": ")     
        return Destinatario, texto_enviar

    def audiorec(self):                                                      #DRRP con este se determina si la duracion de la grabacion
        duracion=input("Cuantos segundos desea grabar:")                     #     es valida
        if int(duracion)>0 and int(duracion)<=30:
            logging.info("Comenzando grabacion...")
            return duracion
        else: 
            logging.warning("Tiempo no valido")
            grabado=False
            return grabado
    
    def audioreproduct(self):                                                 #DRRP se reproduce el ultimo audio entrante
        consola="aplay notaentrante.wav"
        os.system(consola)

class AudioClass (object):                                                    #Clase con el manejo del audio
    def __init__(self,accion,duracion=0,Destinatario=""):
        self.accion=accion
        self.duracion=duracion
        self.Destinatario=Destinatario
        
        if self.accion==1:
            self.audiorecord(duracion)
            grabado=True
            return grabado
        elif self.accion==2:
            self.enviaraudio(Destinatario)
        else:
            self.audiorepro()
        

    def audiorecord(self,duracion):                                            #DRRP se graba el audio
        consola="arecord -d "+str(duracion)+" -f U8 -r 8000 notadevoz.wav"
        os.system(consola)
        logging.info("Grabacion finalizada")
        #peso=os.stat("notadevoz.wav").st_size

    #def audiorepro(self):                                                     #Metodos no necesarios, no mas
    #    self.pushThread.threading.Thread(name="Reproductor",target=self.transformadorAudi,args=(),daemon=False)
    #    self.pushThread.start()
    
    #def transformadorAudi(self):
    #    consola="aplay notaentrante.wav"
    #    os.system(consola)
    #    self.pushThread._stop()

def enviaraudio(destinatario):                                              #DRRP Para enviar audio se utiliza otro metodo
    #print(destinatario)                                                     #     debido a el tipo de empaquetado que tiene
    audiosaliente=open("notadevoz.wav","rb")
    bitsdeaudio=audiosaliente.read()
    audiosaliente.close()
    byteArray=bytes(bitsdeaudio)
    topic=AUDIO+"/"+str(grupo)+"/"+destinatario
    publishData(topic,byteArray)
    


def Whatsmyname():                                                          #DRRP Identifica quien soy  
    file=open("usuario","r")#ojo este cambia para clientes                  #     y retorna el carné del usuario
    for i in file:
        YoSoy=str(i)
        YoSoy=YoSoy.replace("\n","")
    return YoSoy    

def on_connect(cliente,userdata,flags,rc):                                  #DRRP metodo de MQTT para la conexion con el Broken
    logging.debug("Conexion establecida")

def isAnAudio(source):                                                      #DRRP para saber que tipo de tratamiento se le da al 
    global userid                                                           #     mensaje es necesario saber si es de audio o no
    banderita=False
    if source==AUDIO:
        banderita= True
    return banderita

def leerMensaje ():    
    archivo = open("Archivo_topics", 'r')                                   #RDSS abrimos el archivo mensajes en modo lectura
    for linea in archivo:                                                   #RDSS for para cada line del archivo
        lineaNueva = linea[:5]                                              #RDSS seleccionamos solo los caracteres que esten dentro de este rango
        #registro = lineaNueva.split('b Diego&Simon$ b') #RDSS va a separar cada vez que encuentre una coma
    archivo.close() #Cerramos el archivo
    print(lineaNueva)
    banderita2=isAnAudio(lineaNueva)
    if banderita2:
        logging.info("Ha llegado un nuevo audio")                            #DRRP tratamiento del mensaje 
        bits=open("Archivo_mensajes","rb")
        lectura=bits.read()
        bits.close()
        nuevoaudio=open("notaentrante.wav","wb")
        nuevoaudio.write(lectura)
        nuevoaudio.close()
        reproducir=AudioClass.audiorepro()

    else:
        showMSG=open("Archivo_mensajes","r")
        logging.info("Ha llegado el siguiente mensaje: ")
        for lineaMSG in showMSG:
            
            logging.info(lineaMSG)

##########################################################################
####################        METODOS MQTT           #######################
########################################################################## 
def on_message(client,userdata,msg):
    TopicRecibido ="echo "+str(msg.topic)+" > Archivo_topics"
    os.system(TopicRecibido)
    newmessage=open("Archivo_mensajes","wb")
    newmessage.write(msg.payload)
    newmessage.close()
    leerMensaje()

def on_publish(client, userdata, mid):                                      #DRRP metodo de MQTT para la publicacion
    publishText = "Publicacion satisfactoria"
    logging.debug(publishText)

def confCliente():                                                        #DRRP Hice dos metodos distintos para la publicacion y recepcion
    global clientMQTT                                                #     porque no estoy seguro de si entrarian en conflicto
    clientMQTT=mqtt.Client(clean_session=True)
    clientMQTT.on_connect=on_connect
    clientMQTT.on_message=on_message
    clientMQTT.on_publish=on_publish
    clientMQTT.username_pw_set(MQTT_USER, MQTT_PASS) 
    clientMQTT.connect(host=MQTT_HOST, port = MQTT_PORT) 

def room_subs():                                                            #DRRP el metodo room_subs y user_subs establecen la suscripcion a todo
    file=open("salas","r")#ojo cambiar para los clientes           #     los topics que el usuario tiene que estar suscrito
    finallist=[]
    for i in file:
        newlist=[]
        text=SALAS+"/"+str(grupo)+"/"+str(i)
        text=text.replace("\n","")
        newlist.append(text)
        newlist.append(qos)
        finallist.append(tuple(newlist))
    file.close()
    clientMQTT.subscribe(finallist)

def user_subs():
    global userid
    userid=Whatsmyname()
    text=USUARIOS+"/"+userid
    clientMQTT.subscribe((text,qos))
    text2=AUDIO+"/"+str(grupo)+"/"+userid
    clientMQTT.subscribe((text2,qos))#Nuevo topic agregado a las suscripciones

def recepcion_data():                                                       #DRRP este metodo lo cree para que pueda trabajar en un hilo demonio
    clientMQTT.loop_start()

def publishData(topic,value,qos=0,retain=False):                            #DRRP metodo especial para publicar texto plano
    clientMQTT.publish(topic,value,qos,retain)

##########################################################################
####################        Principal              #######################
##########################################################################
logging.basicConfig(                                                        #DRRP configuracion del logging
    level = logging.INFO, 
    format = '[%(levelname)s] %(message)s'
    )

       #DRRP inicializacion de metodos necesarios
confCliente()
room_subs()
user_subs()

t1=threading.Thread(name="Recepcion",target=recepcion_data,args=(),daemon=True) #DRRP creacion del hilo que recibira mensajes
t1.start()

print("\n\nBienvenido al chat de proyectos980")
try:
    while True:                                                             #DRRP manejo de las instruciones iniciales dentro de un ciclo principal
        instruccion=input("Presiona enter para ver opciones o ingresa un comando: ")
        if instruccion=="\n":
            Instructions.inicial(instruccion)
        elif instruccion=="1a": #Mensaje Directo
            destin, mensaje=Instructions.direct(instruccion)
            topic=USUARIOS+"/"+destin
            publishData(topic,mensaje)
        elif instruccion=="1b": #Mensaje a grupo
            destin, mensaje=Instructions.grupo(instruccion)
            topic=SALAS+"/"+str(grupo)+"/"+destin
            publishData(topic,mensaje)
        elif instruccion=="2": #Audio
            Destinatario=input("Destinatario:")
            subtopic=Whatsmyname()
            subtopic=str(grupo)+"/"+subtopic
            duracion=Instructions.audiorec(instruccion)
            grabado=AudioClass.audiorecord(1,duracion)
            print("Se enviara el audio a: "+Destinatario )
            enviaraudio(destinatario=Destinatario)

        elif instruccion=="3":  #Reproducir Audio
            Instructions.audioreproduct(instruccion)
        elif instruccion=="4":  #Menu
            Instructions.inicial(instruccion)
        elif instruccion=="5":   #Desconectarme
            clientMQTT.disconnect()
            sys.exit()
        else:
            print("Ingrese un comando válido, Ej: \'1a\'")
            Instructions.inicial(instruccion)

except KeyboardInterrupt:
    logging.info("\nTerminando conexion")
    if t1.is_alive():
        t1._stop()
    
finally:
    clientMQTT.disconnect()
    sys.exit()