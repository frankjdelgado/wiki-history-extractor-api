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
    """
    Return list of article revisions

    Pagination:
    <ul class="params">
        <li>page: Page number. Defaults to 1.</li>
        <li>page_size: Number of items per page. Defaults to 20, max size of 200.</li>
        <li>sort: Sort by timestamps. Example: ?sort=asc or ?sort=desc</li>
        <i>Example: <a href="revisions?title=RabbitMQ&page=1&page_size=5&sort=desc" target="_blank">/api/v1/revisions?page=1&page_size=5&sort=desc</a></i>
    </ul>
    Filters:
    <ul class="params">
        <li>comment</li>
        <li>anon</li>
        <li>pageid</li>
        <li>tags</li>
        <li>timestamp</li>
        <li>userid</li>
        <li>revid</li>
        <li>contentformat</li>
        <li>contentmodel</li>
        <li>extraction_date</li>
        <li>parentid</li>
        <li>title</li>
        <li>_id</li>
        <li>size</li>
        <li>user</li>
        <li>minor</li>
        <li>*</li>
        <i>Example: <a href="revisions?title=RabbitMQ" target="_blank">/api/v1/revisions?title=RabbitMQ&page=1&page_size=5&sort=desc</a></i>
    </ul>
    Project: Decide which columns to show
    <ul class="params">
        <li>comment</li>
        <li>anon</li>
        <li>pageid</li>
        <li>tags</li>
        <li>timestamp</li>
        <li>userid</li>
        <li>revid</li>
        <li>contentformat</li>
        <li>contentmodel</li>
        <li>extraction_date</li>
        <li>parentid</li>
        <li>title</li>
        <li>_id</li>
        <li>size</li>
        <li>user</li>
        <li>minor</li>
        <li>*</li>
        <i>Example: <a href="revisions?title=RabbitMQ&project=title,revid,timestamp&page=1&page_size=5&sort=desc" target="_blank">/api/v1/revisions?title=RabbitMQ&project=title,revid,timestamp&page=1&page_size=5&sort=desc</a></i>
    </ul>

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
