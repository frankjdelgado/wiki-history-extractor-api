from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api,auto
from .. import db
from vendors.query_handler import QueryHandler
from vendors.db_connector import RevisionDB
from config import config, Config

@api.route('/revs', methods=['GET'])
@auto.doc()
def revs():
    ##PROBANDO AQUI, REVISAR ###
    handler=QueryHandler()
    '''The function execute the queries of the revisions.'''
    if request.args.get('user') != None:
        user = request.args.get('user')
        number= handler.get_count(1000,[user])
        return jsonify({'count':number})
    else:
        return "nada chico!"
