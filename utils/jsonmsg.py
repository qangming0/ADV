#!/usr/bin/python
# -*- coding: utf8 -*-


import json
import io
import string
import random
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

# dictionary
# abc = {'email': 'leila@example.com', 'content': 'foo bar', 'created': '2016-01-27T15:17:10.375877'}
# print(abc)

# bytearrays
# json = JSONRenderer().render(abc)
# print(json)

# object
# stream = io.BytesIO(json)
# print(stream)

# dictionary
# data = JSONParser().parse(stream)
# print(data)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class JsonMessage(object):
    def __init__(self):
        pass

    @staticmethod
    def byte2Dict(bjson):
        if not isinstance(bjson, bytes):
            return None
        return JSONParser().parse(io.BytesIO(bjson))

    @staticmethod
    def dic2Byte(message):
        if not isinstance(message, (dict, int, str)):
            return None
        return JSONRenderer().render(message)

    @staticmethod
    def decode(message):
        if not isinstance(message, (str)):
            return None
        return json.loads(message)

    @staticmethod
    def encode(message):
        if not isinstance(message, (dict, list)):
            return None
        return json.dumps(message)