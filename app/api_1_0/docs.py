from flask import Flask, request, Response
from . import api

@api.route('/', methods=['GET'])
def docs():
    return "This is a Docs page!"