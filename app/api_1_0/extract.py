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

    Example: <a href="extract?title=RabbitMQ&locale=es" target="_blank">/api/v1/extract?title=RabbitMQ&locale=es</a>

    Params:
    <ul class="params">
        <li>title: Article Title. <i>Example: RabbitMQ</i></li><li>url: Article URL. <i>Example: <a href="https://es.wikipedia.org/wiki/RabbitMQ" target="_blank">https://es.wikipedia.org/wiki/RabbitMQ</a></i></li><li>locale: Article Language <i>(Optional)</i>. <i>Example: en</i></li>
    </ul>
    '''
    pageid = request.args.get('pageid')
    locale = request.args.get('locale','en')

    if request.args.get('title') != None:
        title = request.args.get('title')
    elif request.args.get('url') != None:
        url_parts = urlparse.urlparse(request.args.get('url'))
        path_parts = url_parts[2].rpartition('/')
        title = path_parts[2]

        domain = request.args.get('url').split('//')[1].split('.')[0]
        if domain !="wikipedia":
            locale = domain
    else:
        response = jsonify(
            {"message": "Unsupported wiki article title or url given"})
        response.status_code = 400
        return response

    task = extract_article.delay(title, locale, pageid)
    return jsonify({'Location': url_for('.task_status',task_id=task.id, name='extract_article', _external=True)}), 202
