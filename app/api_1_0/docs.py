from flask import Flask, Response
from . import api
from flask_autodoc import Autodoc

auto=Autodoc()

@api.route('/', methods=['GET'])
@auto.doc()
def docs():
    '''Shows this Documentation'''
    return auto.html(title='Wiki History Extractor API')
