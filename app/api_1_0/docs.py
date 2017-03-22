from flask import Flask, Response
from . import api


@api.route('/', methods=['GET'])
def docs():
    return "This is a Docs page"