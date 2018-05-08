from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api, filter_params, project_params
from vendors.db_connector import RevisionDB
from config import config, Config
from manage import auto

@api.route('/articles', methods=['GET'])
@auto.doc()
def articles():
    '''
    Return list of articles.

    Pagination:
    - page: Page number. Defaults to 1. Example: ?page=2
    - page_size: Number of items per page. Defaults to 20, max size of 200. Example: ?page=1&page_size=100

    Filters:
    - title
    - ns
    - first_extraction_date
    - last_extraction_date
    - last_revision_extracted
    - locale
    '''

    page = request.args.get('page', 1, int)
    page_size = request.args.get('page_size', 20, int)
    query = filter_params(request)
    project = project_params(request)

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})

    articles=db.articles(query, page, page_size, project)

    return Response(
        json_util.dumps(articles),
        mimetype='application/json'
    )


@api.route('/articles/<page_id>',methods=['GET'])
@auto.doc()
def article(page_id):
    '''Return the article for the given pageid.'''

    project = project_params(request)

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    query={'pageid':int(page_id)}
    art= db.article(query, project) or {}
    return Response(
        json_util.dumps(art),
        mimetype='application/json'
    )
