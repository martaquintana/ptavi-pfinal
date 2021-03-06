#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""SIP uaserver."""
import sys
import os
import socketserver
from uaclient import XML
from uaclient import Log


class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""

    receptor = []

    def handle(self):
        """SIP Handle."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            linea_decod = line.decode('utf-8').split(" ")
            print(linea_decod)
            if('sip:' not in linea_decod[1] or
               '@' not in linea_decod[1] or
               'SIP/2.0' not in linea_decod[2]):
                mensaje = ('SIP/2.0 400 Bad Request\r\n\r\n')
                self.wfile.write(bytes(mensaje, "utf-8"))
                Log.appendlog('Error: ' + mensaje, LOG_PATH)
                Log.appendlog(
                    'Send to ' +
                    self.client_address[0] + ':' +
                    str(self.client_address[1]) + ': ' +
                    mensaje, LOG_PATH)
                break

            metodo = linea_decod[0]
            if metodo == 'INVITE':
                if len(self.receptor) != 0:
                    # borra la ip anterior que se habia guardado
                    self.receptor.pop(0)
                    # borra el puerto anterior que se habia guardado
                    self.receptor.pop(0)

                self.receptor.append(linea_decod[-4].split()[0])
                self.receptor.append(linea_decod[-2])
                recv_message = ' '.join(linea_decod)
                Log.appendlog('Received from ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              recv_message, LOG_PATH)
                print(self.receptor)
                sdp = ('Content-Type: application/sdp\r\n\r\n' + 'v=0\r\n' +
                       'o=' + DIC_CONFIG['account_username'] +
                       ' ' + DIC_CONFIG['uaserver_ip'] +
                       '\r\n' + 's= Christmas\r\n' + 't=0\r\n' + 'm=audio ' +
                       DIC_CONFIG['rtpaudio_puerto'] + ' RTP\r\n')

                mensaje = ('SIP/2.0 100 Trying\r\n\r\n' +
                           'SIP/2.0 180 Ringing\r\n\r\n' +
                           'SIP/2.0 200 OK\r\n\r\n' + sdp)
                self.wfile.write(bytes(mensaje, "utf-8"))
                Log.appendlog('Send to ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              mensaje, LOG_PATH)
                break

            if metodo == 'ACK':
                """ aejecutar es un string con lo que se ha
                    de ejecutar en la shell.
                """
                receptor_ip = self.receptor[0]
                receptor_puerto = self.receptor[1]
                print(receptor_puerto)
                print(receptor_ip)
                recv_message = ' '.join(linea_decod)
                Log.appendlog('Received from ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              recv_message, LOG_PATH)
                fichero_audio = DIC_CONFIG["audio_path"]
                aejecutar = ("./mp32rtp -i " +
                             receptor_ip + " -p " + receptor_puerto)
                aejecutar += " < " + fichero_audio
                print("Vamos a ejecutar", aejecutar)
                os.system(aejecutar)
                print("cancion.mp3 enviada desde servidor")
                break

            if metodo == 'BYE':
                recv_message = ' '.join(linea_decod)
                Log.appendlog('Received from ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              recv_message, LOG_PATH)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                Log.appendlog('Send to ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              'SIP/2.0 200 OK\r\n\r\n', LOG_PATH)
                print(self.client_address)
                break

            if metodo != 'INVITE' or metodo != 'BYE' or metodo != 'ACK':
                mensaje = ('SIP/2.0 405 Method Not Allowed\r\n\r\n')
                self.wfile.write(bytes(mensaje, "utf-8"))
                Log.appendlog('Error: ' + mensaje, LOG_PATH)
                Log.appendlog('Send to ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              mensaje, LOG_PATH)
                break
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break


if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        FICHERO = sys.argv[1]
        LEERXML = XML(FICHERO)
        DIC_CONFIG = XML.get_diccionario(LEERXML)
        print(DIC_CONFIG)
        print(DIC_CONFIG['account_username'])
        LOG_PATH = DIC_CONFIG['log_path']
        Log.appendlog('Starting...', LOG_PATH)
        SERV = socketserver.UDPServer((DIC_CONFIG['uaserver_ip'],
                                       int(DIC_CONFIG['uaserver_puerto'])),
                                      SIPHandler)
        print("Listening...")
        try:
            SERV.serve_forever()
        except KeyboardInterrupt:
            Log.appendlog('Finishing.', LOG_PATH)
            print("Finalizado servidor")
    except (IndexError, ValueError, PermissionError or len(sys.argv) < 2):
        print("Usage: phython3 uaserver.py config")
