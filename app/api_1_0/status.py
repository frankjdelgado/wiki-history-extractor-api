from flask import Flask, request, jsonify, Response, url_for
from ...vendors.api_extractor import RevisionExtractor
from ...vendors.db_connector import RevisionDB
import urlparse
from bson import json_util
from . import api

@api.route('/status/<task_id>')
def taskstatus(task_id):
    name = request.form.get('name')

    if name == "hello":
        task = hello.AsyncResult(task_id)

    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)