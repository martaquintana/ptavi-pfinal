#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import socketserver
from uaclient import XMLHandler
from uaclient import XML
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""
    receptor = []
    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea_decod = line.decode('utf-8').split(" ")
            print(linea_decod)
            if ('sip:' not in linea_decod[1] or
                    '@' not in linea_decod[1] or
                    'SIP/2.0' not in linea_decod[2]):
                        self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                        break

            metodo = linea_decod[0]
            if metodo == 'INVITE':
                self.receptor.append(linea_decod[-4].split()[0])
                self.receptor.append(linea_decod[-2])
                print(self.receptor)
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                sdp = ('Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n' +
                         'o=' + DIC_CONFIG['account_username'] + ' ' + DIC_CONFIG['uaserver_ip'] +
                         '\r\n' + 's= Christmas\r\n' + 't=0\r\n' + 'm=audio ' +
                         DIC_CONFIG['rtpaudio_puerto'] + ' RTP\r\n')
                self.wfile.write(bytes(sdp,"utf-8"))
                break

            if metodo == 'ACK':
                # aEjecutar es un string con lo que se ha de ejecutar en la shell
                receptor_IP = self.receptor[0]
                receptor_Puerto = self.receptor[1]
                print(receptor_Puerto)
                print(receptor_IP)
                fichero_audio = DIC_CONFIG["audio_path"]
                aEjecutar = "./mp32rtp -i " + receptor_IP + " -p " + receptor_Puerto
                aEjecutar += " < " + fichero_audio
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)  
                self.wfile.write(b"cancion.mp3 enviada desde servidor")
                break
                #REVISAR PUERTOS! LEER SDP o dejarlo con lo de la configuracion porque es igual??

            if metodo == 'BYE':
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                break

            if metodo != 'INVITE' or metodo != 'BYE' or metodo != 'ACK':
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
                break
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break



if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        fichero = sys.argv[1]
        leerxml = XML(fichero)
        DIC_CONFIG= XML.get_diccionario(leerxml)
        print(DIC_CONFIG)
        print(DIC_CONFIG['account_username'])
        serv = socketserver.UDPServer((DIC_CONFIG['uaserver_ip'], int(DIC_CONFIG['uaserver_puerto']) ), SIPHandler)
        print("Listening...")
        try:
            serv.serve_forever()
        except KeyboardInterrupt:
            print("Finalizado servidor")
    except (IndexError, ValueError, PermissionError or len(sys.argv)< 2):
        print("Usage: phython3 uaserver.py config")

   
