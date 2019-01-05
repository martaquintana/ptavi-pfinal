#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socketserver
import socket
import json
from uaclient import XMLHandler
from uaclient import XML
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import hashlib
import random
from uaclient import Log


class SIPHandler(socketserver.DatagramRequestHandler):
    """SIP server class."""

    dic_registrados = {}
    dic_clients = {}
    expires = '0'
    user_invited = []

    def register2json(self):
        """JSON file."""
        json.dump(self.dic_clients, open(DIC_CONFIG['database_path'], 'w'))

    def json2register(self):
        """Open JSON file and gets the dictionary."""
        with open(DIC_CONFIG['database_passwdpath'], 'r') as fich:
            self.dic_registrados = json.load(fich)
        print(self.dic_registrados)

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
                port = client_sip[-1]
                self.json2register()
                self.dic_clients[sip_address] = {
                                            "address": self.client_address[0],
                                            "port": port, }
                message_recv = ' '.join(linea_decod)
                Log.appendlog('Received from ' + self.client_address[0] + ':' +
                              str(self.client_address[1]) + ': ' +
                              message_recv, LOG_PATH)

                if (sip_address in self.dic_clients and
                   'Authorization:' in linea_decod):
                    response = linea_decod[8]
                    print (response)
                    m = hashlib.sha224(bytes(self.dic_registrados[sip_address],
                                             'utf-8'))
                    m.update(bytes(NONCE, 'utf-8'))
                    response_proxy = m.hexdigest()
                    print(response_proxy)
                    if response == response_proxy:
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                        Log.appendlog('Send to ' +
                                      self.client_address[0] + ':' +
                                      str(self.client_address[1]) + ': ' +
                                      'SIP/2.0 200 OK\r\n\r\n', LOG_PATH)
                    else:
                        mensaje = ('ERROR Authorization invalid\r\n\r\n')
                        self.wfile.write(bytes(mensaje, "utf-8"))
                        Log.appendlog('Error: ' + mensaje, LOG_PATH)
                        Log.appendlog('Send to ' + self.client_address[0] +
                                      ':' + str(self.client_address[1]) +
                                      ': ' + mensaje, LOG_PATH)

                else:
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n" +
                                     b"WWW Authenticate: Digest " +
                                     b"nonce= " + bytes(NONCE, "utf-8") +
                                     b"\r\n\r\n")
                    Log.appendlog('Send to ' + self.client_address[0] + ':' +
                                  str(self.client_address[1]) + ': ' +
                                  'SIP/2.0 401 Unauthorized\r\n' +
                                  'WWW Authenticate: Digest ' +
                                  'nonce= ' + NONCE + '\r\n\r\n', LOG_PATH)

                if('sip:' not in linea_decod[1] or
                   '@' not in linea_decod[1] or
                   'SIP/2.0' not in linea_decod[2]):
                        mensaje = ('SIP/2.0 400 Bad Request\r\n\r\n')
                        self.wfile.write(bytes(mensaje, "utf-8"))
                        Log.appendlog('Error: ' + mensaje, LOG_PATH)
                        Log.appendlog('Send to ' + self.client_address[0] +
                                      ':' + str(self.client_address[1]) +
                                      ': ' + mensaje, LOG_PATH)
                        break

                if linea_decod[3] == 'Expires:':
                    try:
                        print("HEEEY")
                        expires = linea_decod[4]
                        print(expires)
                        then = time.strftime(
                               '%Y-%m-%d %H:%M:%S', time.gmtime(
                                      time.time() + float((expires))))
                        print(then)
                        self.dic_clients[sip_address][
                            "fecha_registro"] = time.time()
                        self.dic_clients[sip_address][
                            "tiempo_expiracion"] = expires
                        self.dic_clients[sip_address][
                            "expires"] = then
                        if expires == '0':
                            del self.dic_clients[sip_address]
                        else:
                            self.whohasexpired()
                    except ValueError:
                        mensaje = ('Error expires must be a number')
                        self.wfile.write(bytes(mensaje, "utf-8"))
                        print(mensaje)
                        Log.appendlog('Error: ' + mensaje, LOG_PATH)
                        Log.appendlog('Send to ' + self.client_address[0] +
                                      ':' + str(self.client_address[1]) +
                                      ': ' + mensaje, LOG_PATH)
                        break

            if METODO == "INVITE":
                self.user_invited.append(linea_decod[1].split(":")[1])

            if METODO != "REGISTER":
                """ EL PROXY TODO LO QUE LE LLEGA LO MANDA,
                Y EL SERVER CONTESTA con los errores"""
                try:
                    user = self.user_invited[0]
                    self.whohasexpired()
                    print(user)
                    if user in self.dic_clients and user != '':
                        print("si!! el usuario está registrado")
                        try:
                            with socket.socket(socket.AF_INET,
                                               socket.SOCK_DGRAM) as my_socket:
                                my_socket.setsockopt(socket.SOL_SOCKET,
                                                     socket.SO_REUSEADDR, 1)
                                my_socket.connect((
                                        self.dic_clients[user]["address"],
                                        int(self.dic_clients[user]["port"])))
                                Log.appendlog('Received from ' +
                                              self.client_address[0] +
                                              ':' +
                                              str(self.client_address[1]) +
                                              ': ' +
                                              line.decode("utf-8"), LOG_PATH)
                                send_message = line
                                print (send_message)
                                my_socket.send(send_message)
                                message_send = ' '.join(linea_decod)
                                Log.appendlog(
                                    'Send to ' +
                                    self.dic_clients[user]["address"] +
                                    ':' + self.dic_clients[user]["port"] +
                                    ': ' + message_send, LOG_PATH)
                                recv_message = my_socket.recv(1024)
                                print(recv_message)
                                Log.appendlog(
                                    'Received from ' +
                                    self.dic_clients[user]["address"] +
                                    ':' + self.dic_clients[user]["port"] +
                                    ': ' +
                                    recv_message.decode("utf-8"), LOG_PATH)
                                self.wfile.write(recv_message)
                                Log.appendlog(
                                    'Send to ' +
                                    self.client_address[0] + ':' +
                                    str(self.client_address[1]) + ': ' +
                                    recv_message.decode("utf-8"), LOG_PATH)
                        except ConnectionRefusedError:
                            error = (
                                b"No server listening at " +
                                bytes(self.dic_clients[user]["address"],
                                      "utf-8") +
                                b" port " +
                                bytes(self.dic_clients[user]["port"], "utf-8"))
                            self.wfile.write(error)
                            print(error)
                            Log.appendlog('Error: ' +
                                          error.decode("utf-8"), LOG_PATH)
                            Log.appendlog('Send to ' +
                                          self.client_address[0] +
                                          ':' + str(self.client_address[1]) +
                                          ': ' +
                                          error.decode("utf-8"), LOG_PATH)

                    else:
                        mensaje = 'SIP/2.0 404 User Not Found\r\n\r\n'
                        self.wfile.write(bytes(mensaje, "utf-8"))
                        Log.appendlog('Error: ' + mensaje, LOG_PATH)
                        Log.appendlog('Send to ' + self.client_address[0] +
                                      ':' + str(self.client_address[1]) +
                                      ': ' + mensaje, LOG_PATH)
                        break
                except IndexError:
                    mensaje = 'Error You can not say Bye without an Invite'
                    self.wfile.write(bytes(mensaje, "utf-8"))
                    print(mensaje)
                    Log.appendlog('Error: ' + mensaje, LOG_PATH)
                    Log.appendlog('Send to ' + self.client_address[0] +
                                  ':' + str(self.client_address[1]) +
                                  ': ' + mensaje, LOG_PATH)
                    break

            print("Nuevo usuario registrado")
            self.register2json()
            print(self.dic_clients)
            break


if __name__ == "__main__":
    """
    Programa principal
    """
    try:
        NONCE = str(random.randrange(10000000000))
        """
        Cada vez que se inicia el proxy_registrar,
        el Nonce es distinto y aleatorio.
        """
        fichero = sys.argv[1]
        leerxml = XML(fichero)
        DIC_CONFIG = XML.get_diccionario(leerxml)
        if DIC_CONFIG['server_ip'] == '':
            DIC_CONFIG['server_ip'] = '127.0.0.1'
        print(DIC_CONFIG)
        LOG_PATH = DIC_CONFIG['log_path']
        # print(DIC_CONFIG['server_name'])
        Log.appendlog('Starting...', LOG_PATH)
        serv = socketserver.UDPServer((DIC_CONFIG['server_ip'],
                                       int(DIC_CONFIG['server_puerto'])),
                                      SIPHandler)
        print("Server MiServidorBigBang listening at port " +
              DIC_CONFIG['server_puerto'] + "...")
        try:
            serv.serve_forever()

        except KeyboardInterrupt:
            Log.appendlog('Finishing.', LOG_PATH)
            print("Finalizado servidor")
    except (IndexError, ValueError, PermissionError or len(sys.argv) < 2):
        print("Usage: phython3 proxy_registrar.py config")
    except (FileNotFoundError or NameError):
        print("Usage: phython3 proxy_registrar.py config")
