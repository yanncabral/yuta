from threading import Thread, Timer
from pymongo import MongoClient
import serial
import pyttsx3
from datetime import datetime, timedelta
from app.database import database
from time import sleep

global antes
antes = datetime.now()

# client = MongoClient("localhost",27017)
# db = client['casa']
dispositivos_collection = database['devices']
alertas_collection = database['alertas']
meu_serial = None
sleep(2)

def acao_rgb(nome_dispositivo,acao,cores=None):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo, 'type': 'rgb'})
    pinos = list(dispositivo['pin'])

    if cores == None:
        cores=[255,255,255] #padrão é branco

    if acao.upper() == "ACENDER":
        comando = str(acao).upper() + " RGB " + str(cores[0]) + " "  + str(cores[1]) + " " + str(cores[2]) + " " + str(pinos[0]) + " " + str(pinos[1]) + " " + str(pinos[2]) + "\n"
        print(comando)
        #meu_serial.write(comando.encode("UTF-8"))
        return
    elif acao.upper() == "APAGAR":
        comando = str(acao).upper() + " RGB " + str(pinos[0]) + " " + str(pinos[1]) + " " + str(pinos[2]) + "\n"
        print(comando)
        #meu_serial.write(comando.encode("UTF-8"))
        return

def acao_led(nome_dispositivo,acao):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo, 'type': 'led'})
    pinos = list(dispositivo['digital_pins'])
    if acao.upper() == "LIGAR":
        acao = "ACENDER"
    comando = "CONFIG LED " + str(pinos[0]) + "\n"
    meu_serial.write(comando.encode("UTF-8"))
    comando = str(acao).upper() + " LED " + str(pinos[0]) + "\n"
    print(comando)
    meu_serial.write(comando.encode("UTF-8"))
    return

def acao_ventilador(nome_dispositivo,acao,velocidade=None):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo, 'type': 'fan'})
    pinos = list(dispositivo['pin'])

    if velocidade == None:
        velocidade = 170 #padrão é velocidade média
    else:
        velocidade *= 85 #velocidade dividida em 3

    if acao.upper()  == "LIGAR":
        comando = str(acao).upper()  + " VENTILADOR " + str(velocidade) + " " + str(pinos[0]) + "\n"
        print(comando)
        #meu_serial.write(comando.encode("UTF-8"))
        return
    elif acao.upper()  == "DESLIGAR":
        comando = str(acao).upper()  + " VENTILADOR " + str(pinos[0]) + "\n"
        print(comando)
        #meu_serial.write(comando.encode("UTF-8"))
        return

def acao_porta(nome_dispositivo,acao):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo, 'type': 'door'})
    pinos = list(dispositivo['pin'])

    comando = str(acao).upper()  + " PORTA " + str(pinos[0]) + str(pinos[1]) + "\n"
    print(comando)
    #meu_serial.write(comando.encode("UTF-8"))
    return

def acao_buzzer(nome_dispositivo,acao):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo, 'type': 'buzzer'})
    pinos = list(dispositivo['pin'])

    comando = str(acao).upper()  + " BUZZER " + str(pinos[0]) + str(pinos[1]) + "\n"

    print(comando)
    #meu_serial.write(comando.encode("UTF-8"))
    return

def acao_spotify():
    return

'''
def passa_codigo(nome_dispositivo,acao,especificacao):
    dispositivo = dispositivos_collection.find_one({'name': nome_dispositivo})
    pinos = list(dispositivo['pin'])

    if not dispositivo:
        print("Não há um dispositivo com esse nome.")
        return None

    if dispositivo["type"] == "RGB":
        if especificacao == None:
            especificacao=[255,255,255] #padrão é branco
        acao_rgb(acao,especificacao,pinos)
        return 

    elif dispositivo["type"] == "LED":
        acao_led(acao,pinos)
        return 

    elif dispositivo["type"] == "VENTILADOR":
        if especificacao == None:
            especificacao = [2] #padrão é velocidade média
        acao_ventilador(acao,especificacao,pinos)
        return 

    return 
'''

def funcTTSX3(text):
    global antes
    agora = datetime.now()
    if agora - timedelta(seconds = 2) > antes and agora.hour > 7 and agora.hour <= 17:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    antes = agora
    return

def ler_serial():
    while True:
        texto_recebido = meu_serial.readline().decode().strip()
        if texto_recebido!= "":
            print(texto_recebido)
            if "MOVIMENTO" in texto_recebido.upper():
                aux = texto_recebido.split(' ')
                pino = int(aux[3])
                dispositivo = dispositivos_collection.find_one({'pin': [pino], 'type': 'pir'})

                comando = "Movimento detectado pelo sensor: " + dispositivo['name']
                funcTTSX3(comando.upper())

    sleep(0.1)

def init_serial():
    global meu_serial
    if not meu_serial:
        meu_serial = serial.Serial("COM4", baudrate=9600, timeout=0.01)
        thread = Thread(target=ler_serial)
        thread.daemon = True
        thread.start()

