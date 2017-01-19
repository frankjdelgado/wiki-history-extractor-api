#!flask/bin/python

from flask import Flask, request, jsonify, Response
from vendors.api_extractor import RevisionExtractor
from vendors.db_connector import RevisionDB
import urlparse
from bson import json_util

app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return "Hello, World!"

@app.route('/extract',methods=['GET','POST'])
def extract():

    if request.form.get('url') != None:
        url_parts = urlparse.urlparse(request.form.get('url'))
        path_parts = url_parts[2].rpartition('/')
        title = path_parts[2]

        extractor = RevisionExtractor(payload={'titles': title})
        extractor.get_all()

        response = jsonify({"message": "Success. Extrating article: " + title})
    elif request.form.get('title') != None:
        title = request.form.get('title')
        RevisionExtractor(payload={'titles': title})

        extractor = RevisionExtractor(payload={'titles': title})
        extractor.get_all()

        response = jsonify({"message": "Success. Extrating article: " + request.form.get('title')})
    else:
        response = jsonify({"message": "Unsupported wiki article title or url given"})
        response.status_code = 400
        return response
    return response

@app.route('/revisions',methods=['GET'])
def revisions():
    try:
        page = int(request.args.get('page',1))
    except ValueError:
        page = 1

    revisions = RevisionDB.paginate(page)
    return Response(
        json_util.dumps(revisions),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True)
