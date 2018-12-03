#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
from xml.sax import make_parser


#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
        self.tag_list = []
        self.etiquetas = self.diccionario.keys()

    def startElement(self, name, attrs):

        dic_tag = {}
        if name in self.etiquetas:
            dic_tag['etiqueta'] = name
            # De esta manera tomamos los valores de los atributos
            for atributo in self.diccionario[name]:
                dic_tag[atributo] = attrs.get(atributo, "")
            self.tag_list.append(dic_tag)

    def get_tags(self):
        return self.tag_list

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
   
