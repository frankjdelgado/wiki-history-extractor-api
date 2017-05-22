from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api,auto
from vendors.db_connector import RevisionDB
from config import config, Config


@api.route('/articles', methods=['GET', 'POST'])
@auto.doc()
def articles_task():
    '''Return the list of articles in the database.'''
    db = RevisionDB(config={'host': Config.MONGO_HOST, 'port': Config.MONGO_PORT, 'username': Config.MONGO_USERNAME, 'password': Config.MONGO_PASSWORD})
    arts=db.find_articles(None)
    #convert the collection of articles to a json response 
    return Response(
        json_util.dumps(arts),
        mimetype='application/json'
    )


@api.route('/articles/<page_id>',methods=['GET', 'POST'])
@auto.doc()
def article_info(page_id):
    '''Return the information of the Article in the database with the given page_id.'''
    db = RevisionDB(config={'host': Config.MONGO_HOST, 'port': Config.MONGO_PORT, 'username': Config.MONGO_USERNAME, 'password': Config.MONGO_PASSWORD})
    query={'pageid':int(page_id)}
    arts=db.find_articles(query)
    return Response(
        json_util.dumps(arts),
        mimetype='application/json'
    )


