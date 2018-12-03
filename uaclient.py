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

    def get_tags(self):
        return self.dic_config

class XML:

    def __init__(self, fichero):
        self.get_tags = []
        self.dicc = {}
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(fichero))
        self.get_tags = cHandler.get_tags()
        print(self.get_tags)
  
if __name__ == "__main__":
    """
    Programa principal
    """
    fichero = sys.argv[1]
    leerxml = XML(fichero)
   
