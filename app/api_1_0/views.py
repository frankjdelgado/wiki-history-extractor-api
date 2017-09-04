from flask import Flask, request, Response, jsonify, url_for
from . import api, auto
from app.tasks.app_tasks import hello
from vendors.db_connector import RevisionDB
from config import config, Config
from bson.json_util import dumps


# Testing routes
@api.route('/hello', methods=['GET'])
#@auto.doc()
def hello_test():
	'''Testing function'''
	task = hello.apply_async()
	return jsonify({'Location': url_for('.task_status',task_id=task.id, name='hello')}), 202

@api.route('/test', methods=['GET'])
#@auto.doc()
def test():
	'''Testing function'''
	db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})

	# Number of revisions to process
	value = dumps(db.db.revisions.find({'_id': 1}))


	# Paginate and format chunks of data
	return jsonify({'value': value}), 200
