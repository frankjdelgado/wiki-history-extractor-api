from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from .errors import bad_request 
from . import api,articles
from .utils import filter_params, mode_param
from app.tasks.app_tasks import count_task, avg_task, mode_task
from manage import auto
from vendors.db_connector import RevisionDB
from config import config, Config
from bson.code import Code

def conditions_query(arguments):
    if len(arguments) < 1:
        return "Must add some arguments, please check the query."

    if 'datestart' in arguments and 'dateend' in arguments:
        if arguments.get('dateend') < arguments.get('datestart'):
            return "The interval of dates must be valid, please check the arguments."

    if 'size' in arguments:
        if int(arguments.get('size')) < 1:
            return "The size must be a positive value, please check the arguments."

    return None


@api.route('/mapreduce', methods=['POST'])
@auto.doc()
def mapreduce():
    '''
    Use a json payload to query map reduce results
    
    - collection. Collection name
    - map. map function code.
    - reduce. reduce function code. 
    '''

    collection = request.args.get('collection', 'revisions')
    full_response = request.args.get('full_response', False)
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})

    query = request.get_json(silent=True)

    map_code = Code(request.args.get('map'))
    reduce_code = Code(request.args.get('reduce'))

    result = db.mapreduce(collection, map_code, reduce_code, full_response, query)
    
    return Response(
        json_util.dumps(result),
        mimetype='application/json'
    )

@api.route('/query', methods=['POST'])
@auto.doc()
def query():
    '''
    Use a json payload to query the collections using the mongoDB aggregate function
    
    Params:
    - collection. Collection name. Defaults to 'revisions'. Example: ?collection=articles
    - date_format. Column date format. Defaults to %Y-%m-%dT%H:%M:%S. Example: ?date_Format=%Y-%m-%dT%H:%M:%S
        
    Json Payload Example:
    [
        { 
            "$match": { 
                "extraction_date": "2017-09-28T02:36:33.452000",
                "pageid": 4606
            }
        },
        { 
            "$project" :{ 
                "pageid": 1 , "timestamp" : 1
            } 
            
        },
       { "$limit" : 5 }
    ]
    '''

    collection = request.args.get('collection', 'revisions')
    date_format = request.args.get('date_format', '%Y-%m-%dT%H:%M:%S')
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD})

    pipeline = request.get_json(silent=True)
    
    result = db.aggregate(collection, pipeline, date_format)
    return Response(
        json_util.dumps(result),
        mimetype='application/json'
    )


@api.route('/count', methods=['GET'])
@auto.doc()
def count():
    '''Execute the count query

    Returns the amount of revisions which match the criteria. 

    The function can receive several parameters to filtering the results:
    -title: the name of the wiki article of the revisions.
    -pageid: the id of the wiki article of the revisions.
    -user: the name of the Author of the revisions.
    -userid: the id of the Author of the revisions.
    -tag: a given tag of the revision.
    -size: the size of the revision.
    -sizematch: Used with size filtering, to match the revisions greater , lesser or exact size as given.
    -date: a given date for match revisions made that date.
    -datestart: date from which will match the revisions. If there is not dateend as arg, dateend would be consider the current date.
    -dateend: date until which will match the revisions. If there is not datestart as arg, datestart would be consider the date of the first revision entered.
    (Note: Dates will be displayed in format YYYY-MM-DD)
    '''

    arguments=filter_params(request)
    error_message=conditions_query(arguments)
    if error_message != None:
        return bad_request(error_message)

    #call the task with celery, passing the code to filter by attribute and the list of values(used by get_count)
    task= count_task.delay(arguments)
    result=task.get()
    if 'count' in result:
        return jsonify({'count':result['count']}), 202
    else:
        return bad_request("There was an error with the arguments, please check the query.")

@api.route('/avg', methods=['GET'])
@auto.doc()
def avg():
    '''Execute the average query

    Returns the average of revisions which match the criteria between 2 dates.

    The function can receive one or more criteria to filtering the results, besides the dates of the interval:
    -title: the name of the wiki article of the revisions. 
    -pageid: the id of the wiki article of the revisions.
    -user: the name of the Author of the revisions. 
    -userid: the id of the Author of the revisions.
    -tag: a given tag of the revision. 
    -size: the size of the revision. 
    -sizematch: Used with size filtering, to match the revisions greater, lesser or exact size as given. 

    An explicit date interval is necessary for the query: (Dates will be in format YYYY-MM-DD) 
    -datestart: initial date of the interval from which will match the revisions. 
    -dateend: final date of the interval until which will match the revisions.
    '''

    arguments=filter_params(request)
    error_message=conditions_query(arguments)
    if error_message != None:
        return bad_request(error_message)   

    if not ('datestart' in request.args and 'dateend' in request.args):
        return bad_request("The query must have 'datestart' and 'dateend' arguments, please check the query.")

    task= avg_task.delay(arguments)
    result=task.get()
    if 'avg' in result:
        return jsonify({'avg':result['avg']}), 202
    else:
        return bad_request("There was an error with the arguments, please check the query.")

@api.route('/mode', methods=['GET'])
@auto.doc()
def mode():
    '''Execute the mode query

    Returns the value or values of most repetitions from the revisions, given an attribute. 

    The function receive ONE CRITERIA as mode attribute, using the 'attribute' argument, which will contain an argument's name, among the valid arguments there are:
    -title: the name of the wiki article with most revisions.
    -pageid: the id of the wiki article with most revisions.
    -user: the name of the Author(s) which wrote most revisions.
    -userid: the id of the Author(s) which wrote most revisions.
    -size: the size of revision(s) most repeated.
    -date: the date on which most revisions were written.
    For now, mode for tag criteria is disabled, due to lack of tags in revisions.

    The function can also receive filtering arguments to limit the range, as with count function.
    It is recommended be specially careful about filtering the range of the revisions.
    For instance, avoid use unique date filter when using date as mode attribute, because it will return as best scenario the same date(in that case it is better to use a date interval)
    '''
    arguments=filter_params(request)
    error_message=conditions_query(arguments)
    if error_message != None:
        return bad_request(error_message)

    if not 'attribute' in request.args:
        return bad_request("Must have an 'attribute' argument, please check the query.")
    else:
        mode_attribute=mode_param(request)
        if mode_attribute==None:
            return bad_request("The '"+request.args.get('attribute')+"' argument is not whitelisted to be selected as mode, please check the query.")

    task= mode_task.delay(arguments,mode_attribute)
    result=task.get()
    if 'result' in result:
        return jsonify({mode_attribute:result['result']}), 202
    else:
        return bad_request("There was an error with the arguments, please check the query.")

