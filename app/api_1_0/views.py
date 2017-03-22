from flask import Flask, request, Response, jsonify, url_for
from . import api
from app.tasks.app_tasks import hello

@api.route('/hello', methods=['GET'])
def hello_test():
	task = hello.apply_async()
	return jsonify({'Location': url_for('.task_status',task_id=task.id, name='hello')}), 202