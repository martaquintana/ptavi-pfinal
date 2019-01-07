#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib
import time


class Log():
    def appendlog(mensaje, log_path):
        """Add to a fich log messages"""
        now = time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        fich_log = open(log_path, 'a')
        mensaje = mensaje.replace('\r\n', ' ')
        fich_log.write(now + ' ' + mensaje + '\r\n')
        fich_log.close()


class XMLHandler(ContentHandler):

    def __init__(self):
        self.diccionario = {
            "account": ['username', 'passwd'],
            "uaserver": ['ip', 'puerto'],
            "rtpaudio": ['puerto'],
            "regproxy": ['ip', 'puerto'],
            "log": ['path'],
            "audio": ['path'],
            "server": ['name', 'ip', 'puerto'],
            "database": ['path', 'passwdpath'],
            "account1": ['username', 'passwd'],
            "account2": ['username', 'passwd'],
            }
        self.dic_config = {}

    def startElement(self, name, attrs):

        if name in self.diccionario.keys():
            # De esta manera tomamos los valores de los atributos
            for atributo in self.diccionario[name]:
                self.dic_config[name + '_' + atributo] = attrs.get(atributo,
                                                                   "")

    def get_diccionario(self):
        return self.dic_config


class XML:

    def __init__(self, fichero):
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(fichero))
        self.dic_config = XMLHandler.get_diccionario(cHandler)

    def get_diccionario(self):
        return self.dic_config


if __name__ == "__main__":
    """
    Programa principal
    """

    try:
        CONFIG = sys.argv[1]
        METODO = sys.argv[2]
        OPCION = sys.argv[3]
        LEERXML = XML(CONFIG)
        DIC_CONFIG = XML.get_diccionario(LEERXML)
        print(DIC_CONFIG)
        print(DIC_CONFIG['account_username'])
        DATA_LIST = []
        LOG_PATH = DIC_CONFIG['log_path']
        Log.appendlog('Starting...', LOG_PATH)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((DIC_CONFIG['regproxy_ip'],
                               int(DIC_CONFIG['regproxy_puerto'])))
            print(METODO)
            if METODO == 'REGISTER':
                LINE = ('REGISTER sip:' + DIC_CONFIG['account_username'] +
                        ':' + DIC_CONFIG['uaserver_puerto'] +
                        ' SIP/2.0\r\n' + 'Expires: ' + OPCION + '\r\n\r\n')
                print("Enviando:", LINE)
                Log.appendlog('Send to ' + DIC_CONFIG['regproxy_ip'] + ':' +
                              DIC_CONFIG['regproxy_puerto'] + ': ' +
                              LINE, LOG_PATH)
                my_socket.send(bytes(LINE, 'utf-8'))
                DATA = my_socket.recv(1024)
                RECV_MESSAGE = DATA.decode('utf-8')
                DATA_LIST += RECV_MESSAGE
                print('Recibido -- ', RECV_MESSAGE)
                Log.appendlog('Received from ' +
                              DIC_CONFIG['regproxy_ip'] + ':' +
                              DIC_CONFIG['regproxy_puerto'] + ': ' +
                              RECV_MESSAGE, LOG_PATH)

                if 'nonce' in DATA.decode('utf-8'):
                    nonce = DATA.decode('utf-8').split()[-1].split('=')[-1]
                    M = hashlib.sha224(bytes(DIC_CONFIG['account_passwd'],
                                             'utf-8'))
                    M.update(bytes(nonce, 'utf-8'))
                    RESPONSE = M.hexdigest()
                    print(nonce)
                    print(RESPONSE)
                    LINE = ('REGISTER sip:' + DIC_CONFIG['account_username'] +
                            ':' + DIC_CONFIG['uaserver_puerto'] +
                            ' SIP/2.0\r\n' + 'Expires: ' + OPCION + '\r\n' +
                            'Authorization: Digest response= ' +
                            RESPONSE + '\r\n\r\n')
                    print("Enviando:", LINE)
                    my_socket.send(bytes(LINE, 'utf-8'))
                    Log.appendlog('Send to ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  LINE, LOG_PATH)
                    DATA = my_socket.recv(1024)
                    RECV_MESSAGE = DATA.decode('utf-8')
                    print('Recibido -- ', RECV_MESSAGE)
                    Log.appendlog('Received from ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  RECV_MESSAGE, LOG_PATH)

            if METODO == 'INVITE' or METODO == 'BYE':
                if METODO == 'BYE':
                    LINE = (METODO + ' sip:' + sys.argv[-1] + ' SIP/2.0\r\n')
                    print(LINE)
                    my_socket.send(bytes(LINE, 'utf-8'))
                    Log.appendlog('Send to ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  LINE, LOG_PATH)
                    DATA = my_socket.recv(1024)
                    RECV_MESSAGE = DATA.decode('utf-8')
                    DATA_LIST += RECV_MESSAGE
                    print('Recibido -- ', RECV_MESSAGE)
                    Log.appendlog('Received from ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  RECV_MESSAGE, LOG_PATH)

                if METODO == 'INVITE':
                    LINE = (METODO + ' sip:' + sys.argv[-1] + ' SIP/2.0\r\n' +
                            'Content-Type:' + ' application/sdp\r\n' +
                            'v=0\r\n' + 'o=' + DIC_CONFIG['account_username'] +
                            ' ' + DIC_CONFIG['uaserver_ip'] + '\r\n' +
                            's= Christmas\r\n' + 't=0\r\n' + 'm=audio ' +
                            DIC_CONFIG['rtpaudio_puerto'] + ' RTP\r\n')
                    print(LINE)
                    my_socket.send(bytes(LINE, 'utf-8'))
                    Log.appendlog('Send to ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  LINE, LOG_PATH)
                    DATA = my_socket.recv(1024)
                    RECV_MESSAGE = DATA.decode('utf-8')
                    DATA_LIST += RECV_MESSAGE
                    print('Recibido -- ', RECV_MESSAGE)
                    Log.appendlog('Received from ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  RECV_MESSAGE, LOG_PATH)
            elif METODO != ('REGISTER' or 'INVITE' or 'BYE'):
                print("Solo puedes enviar Métodos REGISTER, INVITE o BYE")

            DATOS = ''.join(DATA_LIST)
            # print(DATOS.split())
            if (DATOS.split()[0] != 'No' and DATOS.split()[1] != '404' and
               DATOS.split()[0] != 'Error'):
                if METODO == 'INVITE' and DATOS.split()[7] == '200':
                    print ("entra en ACK")
                    RECEPTOR_SERVER_IP = DATOS.split()[13]
                    RECEPTOR_SERVER_PUERTO = DATOS.split()[18]
                    print(RECEPTOR_SERVER_PUERTO)
                    print(RECEPTOR_SERVER_IP)
                    LINEA = ('ACK' + ' sip:' +
                             DIC_CONFIG['account_username'] +
                             ' SIP/2.0\r\n\r\n')
                    my_socket.send(bytes(LINEA, 'utf-8'))
                    Log.appendlog('Send to ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  LINEA, LOG_PATH)
                    DATA = my_socket.recv(1024)
                    print("ESTO MANDA EL SERVER", DATA.decode('utf-8'))
                    RECV_MESSAGE = DATA.decode('utf-8')
                    Log.appendlog('Received from ' +
                                  DIC_CONFIG['regproxy_ip'] + ':' +
                                  DIC_CONFIG['regproxy_puerto'] + ': ' +
                                  RECV_MESSAGE, LOG_PATH)
                    FICHERO_AUDIO = DIC_CONFIG["audio_path"]
                    AEJECUTAR = ("./mp32rtp -i " +
                                 RECEPTOR_SERVER_IP + " -p " +
                                 RECEPTOR_SERVER_PUERTO)
                    AEJECUTAR += " < " + FICHERO_AUDIO
                    print("Vamos a ejecutar", AEJECUTAR)
                    os.system(AEJECUTAR)
                    print("Cancion enviada desde cliente")

        Log.appendlog('Finishing.', LOG_PATH)
        print("Socket terminado.")

    except (IndexError, ValueError or len(sys.argv) < 3):
        print("Usage: python3 uaclient.py config metodo opcion")

    except ConnectionRefusedError:
        ERROR = ("No server listening at " + DIC_CONFIG['regproxy_ip'] +
                 " port " + DIC_CONFIG['regproxy_puerto'])
        print(ERROR)
        Log.appendlog('Error: ' + ERROR, LOG_PATH)
