#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaclient import XMLHandler

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
   
