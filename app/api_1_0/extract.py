from flask import Flask, request, jsonify, Response, url_for
from ...vendors.api_extractor import RevisionExtractor
from ...vendors.db_connector import RevisionDB
import urlparse
from bson import json_util
from . import api

@api.route('/extract', methods=['GET', 'POST'])
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

        response = jsonify(
            {"message": "Success. Extrating article: " + request.form.get('title')})
    else:
        response = jsonify(
            {"message": "Unsupported wiki article title or url given"})
        response.status_code = 400
        return response
    return response