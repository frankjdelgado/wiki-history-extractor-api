from flask import Flask, request, jsonify, Response, url_for
from ...vendors.api_extractor import RevisionExtractor
from ...vendors.db_connector import RevisionDB
import urlparse
from bson import json_util
from . import api

@api.route('/revisions', methods=['GET'])
def revisions():
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    revisions = RevisionDB.paginate(page)
    return Response(
        json_util.dumps(revisions),
        mimetype='application/json'
    )
