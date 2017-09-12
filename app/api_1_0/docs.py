from flask import Flask, Response
from . import api
from manage import auto

@api.route('/', methods=['GET'])
@auto.doc()
def docs():
    '''Shows this Documentation'''
    return auto.html(title='Wiki History Extractor API', template="autodoc_custom.html")
