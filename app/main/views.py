import os
from flask import Flask, request, Response, send_from_directory
from . import main

@main.route('/', methods=['GET'])
def index():
    return "Hello World!"

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')