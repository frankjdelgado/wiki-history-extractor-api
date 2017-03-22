from flask import Flask, request, jsonify, Response, url_for
from ...vendors.api_extractor import RevisionExtractor
from ...vendors.db_connector import RevisionDB
import urlparse
from bson import json_util
from . import api

@api.route('/hello', methods=['GET'])
def hello():
    task = hello.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id, name='hello')}
