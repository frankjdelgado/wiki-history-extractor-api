from flask import Flask, request, jsonify, Response, url_for
from app.tasks.app_tasks import extract


import urlparse
from bson import json_util
from . import api

@api.route('/extract', methods=['GET', 'POST'])
def extract():

    if request.form.get('url') != None:
        url_parts = urlparse.urlparse(request.form.get('url'))
        path_parts = url_parts[2].rpartition('/')
        title = path_parts[2]

    elif request.form.get('title') != None:
        title = request.form.get('title')
    else:
        response = jsonify(
            {"message": "Unsupported wiki article title or url given"})
        response.status_code = 400
        return response

    task = extract.apply_async(title)
    return jsonify({'Location': url_for('.task_status',task_id=task.id, name='extract')}), 202