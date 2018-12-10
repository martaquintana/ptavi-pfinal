#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socketserver
from uaclient import XMLHandler
from uaclient import XML
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""
                
    def handle(self):
        """Contesta a los diferentes metodos SIP que le manda el cliente."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea_decod = line.decode('utf-8').split(" ")
            print(linea_decod)
            METODO = linea_decod[0]
            if (len(linea_decod) != 4 or 'sip:' not in linea_decod[1] or
                    '@' not in linea_decod[1] or
                    'SIP/2.0' not in linea_decod[2]):
                    self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                    break
            if METODO == 'REGISTER':
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest "
                + b"nonce='898989898798989898989'\r\n\r\n")
                break


if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        fichero = sys.argv[1]
        leerxml = XML(fichero)
        DIC_CONFIG= XML.get_diccionario(leerxml)
        
        leerxmlpasswd = XML('passwd.xml')
        DIC_USERS = XML.get_diccionario(leerxmlpasswd)
        
        print(DIC_CONFIG)
        print(DIC_CONFIG['server_name'])
        serv = socketserver.UDPServer((DIC_CONFIG['server_ip'], int(DIC_CONFIG['server_puerto']) ), SIPHandler)
        print("Server MiServidorBigBang listening at port 5555...")
        try:
            serv.serve_forever()
        except KeyboardInterrupt:
            print("Finalizado servidor")
    except (IndexError, ValueError, PermissionError or len(sys.argv)< 2):
        print("Usage: phython3 uaserver.py ua2.xml")

   
