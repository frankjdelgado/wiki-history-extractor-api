from flask import Flask, request, Response, jsonify, url_for
from . import api
from app.tasks.app_tasks import hello
from vendors.db_connector import RevisionDB
from config import config, Config
from bson.json_util import dumps

@api.route('/hello', methods=['GET'])
def hello_test():
	task = hello.apply_async()
	return jsonify({'Location': url_for('.task_status',task_id=task.id, name='hello')}), 202

@api.route('/test', methods=['GET'])
def test():
	db = RevisionDB(config={'host': Config.MONGO_HOST, 'port': Config.MONGO_PORT, 'username': Config.MONGO_USERNAME, 'password': Config.MONGO_PASSWORD})

	# Number of revisions to process
	value = dumps(db.db.revisions.find({'_id': 1}))


	# Paginate and format chunks of data
	return jsonify({'value': value}), 200