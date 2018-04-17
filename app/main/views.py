import os
from flask import Flask, request, send_from_directory, redirect, url_for
from . import main

@main.route('/', methods=['GET'])
def index():
    return redirect(url_for('api.docs'))

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')