from flask import Flask, request, jsonify, Response, url_for
from app.tasks.app_tasks import extract_article

import urlparse
from bson import json_util
from . import api
from manage import auto


@api.route('/extract', methods=['GET', 'POST'])
@auto.doc()
def extract():
    '''
    Extract the revisions data from a wiki article. The function can receive the URL or the wiki title.
    Params:
    - title. Example: RabbitMQ
    - url. Example: https://es.wikipedia.org/wiki/RabbitMQ
    - locale. Optional. Example: en
    '''
    if request.args.get('title') != None:
        title = request.args.get('title')
    elif request.args.get('url') != None:
        url_parts = urlparse.urlparse(request.args.get('url'))
        path_parts = url_parts[2].rpartition('/')
        title = path_parts[2]
    else:
        response = jsonify(
            {"message": "Unsupported wiki article title or url given"})
        response.status_code = 400
        return response

    locale = request.args.get('locale')
    pageid = request.args.get('pageid')

    task = extract_article.delay(title, locale, pageid)
    return jsonify({'Location': url_for('.task_status',task_id=task.id, name='extract_article', _external=True)}), 202

