#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class XMLHandler(ContentHandler):

    def __init__(self):
		
        self.diccionario = {
            "account": ['username', 'passwd'],
            "uaserver": ['ip', 'puerto'],
            "rtpaudio": ['puerto'],
            "regproxy": ['ip', 'puerto'],
            "log": ['path'],
            "audio": ['path']
            }
        self.dic_config = {}

    def startElement(self, name, attrs):

        if name in self.diccionario.keys():
            # De esta manera tomamos los valores de los atributos
            for atributo in self.diccionario[name]:
                self.dic_config[name + '_' + atributo] = attrs.get(atributo, "")

    def get_diccionario(self):
        return self.dic_config

class XML:
	
    def __init__(self, fichero):
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(fichero))
        self.DIC_CONFIG= XMLHandler.get_diccionario(cHandler)
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
        leerxml=XML(CONFIG)
        DIC_CONFIG=XML.get_diccionario(leerxml)
        print(DIC_CONFIG)
        print(DIC_CONFIG['account_username'])
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((DIC_CONFIG['uaserver_ip'], int(DIC_CONFIG['uaserver_puerto'])))
            if METODO == 'REGISTER':
                line = (
                    'REGISTER sip:' + DIC_CONFIG['account_username'] + ':' + '1234'
                     + ' SIP/2.0\r\n' + 'Expires: ' + OPCION + '\r\n')
                print("Enviando:", line)
                my_socket.send(bytes(line, 'utf-8'))
                data = my_socket.recv(1024)
                print('Recibido -- ', data.decode('utf-8'))
				
            if METODO == 'INVITE' or METODO == 'BYE':
                line = (METODO + ' sip:' + DIC_CONFIG['account_username'] + ' SIP/2.0\r\n\r\n')
                print(line)
                my_socket.send(bytes(line, 'utf-8'))
                data = my_socket.recv(1024)
                print(data.decode('utf-8'))
            else:
                print("Solo puedes enviar Métodos REGISTER, INVITE o BYE")

            if METODO == 'INVITE' and data.decode('utf-8').split()[-2] == '200':
                linea = ('ACK' + ' sip:' + DIC_CONFIG['account_username'] + ' SIP/2.0\r\n\r\n')
                my_socket.send(bytes(linea, 'utf-8'))
                data = my_socket.recv(1024)
                print(data.decode('utf-8'))
        print("Socket terminado.")

    except (IndexError, ValueError or len(sys.argv)< 3):
        print("Usage: python3 uaclient.py config metodo opcion")

    except ConnectionRefusedError:
        print("Servidor apagado / Error de puerto. ")
		  
