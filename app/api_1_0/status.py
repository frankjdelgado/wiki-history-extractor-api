from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api
from app.tasks.app_tasks import hello, extract_article
from manage import auto

@api.route('/status/<task_id>')
@auto.doc()
def task_status(task_id):
    '''
    Display the current state for the given task_id.

    <i>Example: <a href="status/e63ff805-ed79-4e69-b805-3dbfdb59df10?name=extract_article" target="_blank">api/v1/status/e63ff805-ed79-4e69-b805-3dbfdb59df10?name=extract_article</a></i>
    '''
    name = request.args.get('name')

    if name == "hello":
        task = hello.AsyncResult(task_id)
    elif name == "extract_article":
        task = extract_article.AsyncResult(task_id)

    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
