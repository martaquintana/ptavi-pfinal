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
            "log": ['path']
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
        """
        Devuelve la lista de etiquetas,
        sus atributos y el contenido de los atributos
        """
        return self.tag_list
       
