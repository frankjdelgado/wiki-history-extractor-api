from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api, filter_params
from vendors.db_connector import RevisionDB
from vendors.query_handler import QueryHandler
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
    '''

    page = request.args.get('page', 1, int)
    page_size = request.args.get('page_size', 20, int)
    query = filter_params(request)
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})
    handler = QueryHandler(db=db)
    query = handler.get_articles_query(query)
    revisions=db.articles(query, page, page_size)
    articles=[]
    for rev in revisions:
        rev['first_extraction_date']= rev['first_extraction_date'].isoformat()
        rev['last_extraction_date']= rev['last_extraction_date'].isoformat()
        articles.append(rev)
    return Response(
        json_util.dumps(articles),
        mimetype='application/json'
    )


@api.route('/articles/<page_id>',methods=['GET'])
@auto.doc()
def article(page_id):
    '''Return the article for the given pageid.'''
    
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})
    query={'pageid':int(page_id)}
    art= db.article(query) or {}
    return Response(
        json_util.dumps(art),
        mimetype='application/json'
    )


