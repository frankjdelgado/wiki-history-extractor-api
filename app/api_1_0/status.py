from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from . import api
from app.tasks.app_tasks import hello, extract_article

@api.route('/status/<task_id>')
def task_status(task_id):
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