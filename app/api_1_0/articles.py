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
    """
    Return list of articles.

    Pagination:
    <ul class="params">
        <li>page: Page number. Defaults to 1.</li>
        <li>page_size: Number of items per page. Defaults to 20, max size of 200.</li>
        <i>Example: <a href="articles?page=1&page_size=100" target="_blank">/api/v1/articles?page=1&page_size=100</a></i>
    </ul>
    Filters:
    <ul class="params">
        <li>title</li>
        <li>ns</li>
        <li>first_extraction_date</li>
        <li>last_extraction_date</li>
        <li>last_revision_extracted</li>
        <li>locale</li>
        <i>Example: <a href="articles?title=RabbitMQ" target="_blank">/api/v1/articles?title=RabbitMQ</a></i>
    </ul>
    Project: Decide which columns to show
    <ul class="params">
        <li>title</li>
        <li>ns</li>
        <li>first_extraction_date</li>
        <li>last_extraction_date</li>
        <li>last_revision_extracted</li>
        <li>locale</li>
        <i>Example: <a href="articles?title=RabbitMQ&project=pageid,title" target="_blank">/api/v1/articles?title=RabbitMQ&project=pageid,title</a></i>
    </ul>
    """

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
    '''
    Return the article for the given pageid.

    Project: Decide which columns to show
    <ul class="params">
        <li>title</li>
        <li>ns</li>
        <li>first_extraction_date</li>
        <li>last_extraction_date</li>
        <li>last_revision_extracted</li>
        <li>locale</li>
        <i>Example: <a href="articles/3787053?project=pageid,title,locale" target="_blank">/api/v1/articles/3787053?project=pageid,title,locale</a></i>
    </ul>
    '''

    project = project_params(request)

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    query={'pageid':int(page_id)}
    art= db.article(query, project) or {}
    return Response(
        json_util.dumps(art),
        mimetype='application/json'
    )
