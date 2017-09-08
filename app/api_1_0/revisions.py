from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api,auto
from vendors.db_connector import RevisionDB
from config import config, Config

@api.route('/revisions', methods=['GET'])
@auto.doc()
def revisions():
    '''
        The function returns the content of the revisions.

        Params:

        - page: Page number. Defaults to 1. Example: ?page=2

        - page_size: Number of items per page. Defaults to 20, max size of 200. Example: ?page=1&page_size=100

        - title: Filter revisions by title. Example ?title=The Witcher

        - pageid: Filter revisions by pageid. Example ?pageid=12456
    '''
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    try:
        page_size = int(request.args.get('page_size', 20))
        if page_size > 250:
            page_size=250
    except ValueError:
        page_size = 20

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})

    # Build query
    query={}
    
    if 'pageid' in request.args:
        query={'pageid':int(request.args.get('pageid'))}

    if 'title' in request.args:
        query={'title':request.args.get('title')}
    
    return Response(
        json_util.dumps(db.revisions(query,page,page_size)),
        mimetype='application/json'
    )

