#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socketserver
import json
from uaclient import XMLHandler
from uaclient import XML
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time

class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""
    
    dic_registrados = {}
    dic_clients = {}
    expires ='0'
   
    def register2json(self):
        """JSON file."""
        json.dump(self.dic_clients, open(DIC_CONFIG['database_path'], 'w'))

    def json2register(self):
        """Open JSON file and gets the dictionary."""
        with open(DIC_CONFIG['database_passwdpath'], 'r') as fich:
             self.dic_registrados = json.load(fich)
    def whohasexpired(self):
        """Search and delete the clients expired."""
        del_list = []
        now = time.strftime(
                            '%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
        for clients in self.dic_clients:
            if self.dic_clients[clients]["expires"] <= now:
                del_list.append(clients)
        for clients in del_list:
            del self.dic_clients[clients]

    def handle(self):
        """Contesta a los diferentes metodos SIP que le manda el cliente."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea_decod = line.decode('utf-8').split()
            
            print(linea_decod)
            METODO = linea_decod[0]
            if METODO == 'REGISTER':
                client_sip = linea_decod[1].split(":")
                sip_address = client_sip[1]
                self.dic_clients[sip_address] = {
                                     "address": self.client_address[0],
                                     "port": self.client_address[1]
                                     }				
                self.json2register()
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n" + b"WWW Authenticate: Digest"
                + b"nonce='898989898798989898989'\r\n\r\n")
                if ('sip:' not in linea_decod[1] or
                    '@' not in linea_decod[1] or
                    'SIP/2.0' not in linea_decod[2]):
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                    break
                
                if linea_decod[3] == 'Expires:':
                    print("HEEEY")
                    expires = linea_decod[4]
                    print(expires)
                    then = time.strftime(
                           '%Y-%m-%d %H:%M:%S', time.gmtime(
                                  time.time() + float((expires))))
                    print (then)
                    self.dic_clients[sip_address]["expires"] = then
                    if expires == '0':
                        del self.dic_clients[sip_address]
                    else:
                        self.whohasexpired()

                elif metodo == "INVITE":
                    print(line_decod[0])
					# mirar a quién invitan en el diccionario de registrados
					# abrirle un socket
					# enviarle lo que he recibido con send
					# recibir respuesta con recv
					# enviar respuesta al otro lado con write
					
            print("Nuevo usuario registrado")
            self.register2json()
            print(self.dic_clients)
            
            break


if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        fichero = sys.argv[1]
        leerxml = XML(fichero)
        DIC_CONFIG= XML.get_diccionario(leerxml)
        with open(DIC_CONFIG['database_passwdpath'], 'r') as file_json:
            dic_users = json.load(file_json)
            print (dic_users)
        
        print(DIC_CONFIG)
        #print(DIC_CONFIG['server_name'])
        serv = socketserver.UDPServer((DIC_CONFIG['server_ip'], int(DIC_CONFIG['server_puerto']) ), SIPHandler)
        print("Server MiServidorBigBang listening at port 5555...")
        try:
            serv.serve_forever()
        except KeyboardInterrupt:
            print("Finalizado servidor")
    except (IndexError, ValueError, PermissionError or len(sys.argv)< 2):
        print("Usage: phython3 uaserver.py ua2.xml")

   
