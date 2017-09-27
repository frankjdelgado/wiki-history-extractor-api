from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api, filter_params
from manage import auto
from vendors.db_connector import RevisionDB
from vendors.query_handler import QueryHandler
from config import config, Config

@api.route('/revisions', methods=['GET'])
@auto.doc()
def revisions():
    """Return list of article revisions
    
    Pagination:
    - page: Page number. Defaults to 1. Example: ?page=2
    - page_size: Number of items per page. Defaults to 20, max size of 200. Example: ?page=1&page_size=100    
    
    Filters:
    - comment
    - anon
    - pageid
    - tags
    - timestamp
    - userid
    - revid
    - contentformat
    - contentmodel
    - extraction_date
    - parentid
    - title
    - _id
    - size
    - user
    - minor
    """
    
    page = request.args.get('page', 1, int)
    page_size = request.args.get('page_size', 20, int)
    query = filter_params(request)
    db = RevisionDB()
    handler = QueryHandler(db=db)
    query = handler.get_query(query)
    revisions=db.revisions(query, page, page_size)
    return Response(
        json_util.dumps(revisions),
        mimetype='application/json'
    )

