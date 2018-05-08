from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api, filter_params, project_params
from manage import auto
from vendors.db_connector import RevisionDB
from config import config, Config

@api.route('/revisions', methods=['GET'])
@auto.doc()
def revisions():
    """Return list of article revisions

    Pagination:
    - page: Page number. Defaults to 1. Example: ?page=2
    - page_size: Number of items per page. Defaults to 20, max size of 200. Example: ?page=1&page_size=100
    - sort: Sort by timestamps. Example: ?sort=asc or ?sort=desc

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
    - *

    Project: Decide which columns to show
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
    - *
    """

    page = request.args.get('page', 1, int)
    page_size = request.args.get('page_size', 20, int)
    sort = request.args.get('sort', 'asc')
    query = filter_params(request)
    project = project_params(request)

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})

    revisions = db.revisions(query, page, page_size, sort, project)

    return Response(
        json_util.dumps(revisions),
        mimetype='application/json'
    )
