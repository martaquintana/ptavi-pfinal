#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import hashlib


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
        self.DIC_CONFIG = XMLHandler.get_diccionario(cHandler)

    def get_diccionario(self):
        return self.DIC_CONFIG


if __name__ == "__main__":
    """
    Programa principal
    """

    try:
        CONFIG = sys.argv[1]
        METODO = sys.argv[2]
        OPCION = sys.argv[3]
        leerxml = XML(CONFIG)
        DIC_CONFIG = XML.get_diccionario(leerxml)
        print(DIC_CONFIG)
        print(DIC_CONFIG['account_username'])
        data_list = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((DIC_CONFIG['regproxy_ip'],
                               int(DIC_CONFIG['regproxy_puerto'])))
            print(METODO)
            if METODO == 'REGISTER':
                print("asdfas")
                line = ('REGISTER sip:' + DIC_CONFIG['account_username'] +
                        ':' + DIC_CONFIG['uaserver_puerto'] +
                        ' SIP/2.0\r\n' + 'Expires: ' + OPCION + '\r\n\r\n')
                print("Enviando:", line)
                my_socket.send(bytes(line, 'utf-8'))
                data = my_socket.recv(1024)
                data_list += data.decode('utf-8')
                print('Recibido -- ', data.decode('utf-8'))

                if 'nonce' in data.decode('utf-8'):
                    nonce = data.decode('utf-8').split()[-1].split('=')[-1]
                    m = hashlib.sha224(bytes(DIC_CONFIG['account_passwd'],
                                             'utf-8'))
                    m.update(bytes(nonce, 'utf-8'))
                    response = m.hexdigest()
                    print(nonce)
                    print(response)
                    line = ('REGISTER sip:' + DIC_CONFIG['account_username'] +
                            ':' + DIC_CONFIG['uaserver_puerto'] +
                            ' SIP/2.0\r\n' + 'Expires: ' + OPCION + '\r\n' +
                            'Authorization: Digest response= ' +
                            response + '\r\n\r\n')
                    print("Enviando:", line)
                    my_socket.send(bytes(line, 'utf-8'))
                    data = my_socket.recv(1024)
                    print('Recibido -- ', data.decode('utf-8'))

            if METODO == 'INVITE' or METODO == 'BYE':
                if METODO == 'BYE':
                    line = (METODO + ' sip:' + sys.argv[-1] + ' SIP/2.0\r\n')
                    print(line)
                    my_socket.send(bytes(line, 'utf-8'))
                    data = my_socket.recv(1024)
                    data_list += data.decode('utf-8')
                    print('Recibido -- ', data.decode('utf-8'))

                if METODO == 'INVITE':
                    line = (METODO + ' sip:' + sys.argv[-1] + ' SIP/2.0\r\n' +
                            'Content-Type:' + ' application/sdp\r\n' +
                            'v=0\r\n' + 'o=' + DIC_CONFIG['account_username'] +
                            ' ' + DIC_CONFIG['uaserver_ip'] + '\r\n' +
                            's= Christmas\r\n' + 't=0\r\n' + 'm=audio ' +
                            DIC_CONFIG['rtpaudio_puerto'] + ' RTP\r\n')
                    print(line)
                    my_socket.send(bytes(line, 'utf-8'))
                    data = my_socket.recv(1024)
                    data_list += data.decode('utf-8')
                    print('Recibido -- ', data.decode('utf-8'))
            elif METODO != ('REGISTER' or 'INVITE' or 'BYE'):
                print("Solo puedes enviar Métodos REGISTER, INVITE o BYE")

            DATOS = ''.join(data_list)
            # print(DATOS.split())
            if DATOS.split()[1] != 'apagado' and DATOS.split()[1] != '404':
                if METODO == 'INVITE' and DATOS.split()[7] == '200':
                    print ("entra en ACK")
                    linea = ('ACK' + ' sip:' +
                             DIC_CONFIG['account_username'] +
                             ' SIP/2.0\r\n\r\n')
                    my_socket.send(bytes(linea, 'utf-8'))
                    data = my_socket.recv(1024)
                    print("ESTO MANDA EL SERVER", data.decode('utf-8'))
                    # LEER SDP QUE MANDE EL SEVER; VER PUERTOS¿?
                    receptor_server_IP = DATOS.split()[13]
                    receptor_server_Puerto = DATOS.split()[17]
                    print(receptor_server_Puerto)
                    print(receptor_server_IP)
                    fichero_audio = DIC_CONFIG["audio_path"]
                    aEjecutar = ("./mp32rtp -i " +
                                 receptor_server_IP + " -p " +
                                 receptor_server_Puerto)
                    aEjecutar += " < " + fichero_audio
                    print("Vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                    print("Cancion enviada desde cliente")

        print("Socket terminado.")

    except (IndexError, ValueError or len(sys.argv) < 3):
        print("Usage: python3 uaclient.py config metodo opcion")

    except ConnectionRefusedError:
        print("Servidor proxy_registrar apagado / Error de puerto. ")
