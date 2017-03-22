from flask import Flask, request, Response
from . import main

@main.route('/', methods=['GET'])
def index():
    return "Hello, World!"