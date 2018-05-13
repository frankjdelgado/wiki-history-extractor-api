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


@api.route('/mapreduce', methods=['POST','GET'])
@auto.doc()
def mapreduce():
    '''
    Use a json payload to query map reduce results

    Params:
    <ul class="params">
        <li>collection.Required. Collection name</li>
        <li>map. Required. map function code</li>
        <li>reduce. Required. reduce function code</li>
    </ul>
    <i>Example: <a href="mapreduce?map=function(){emit(this.user,this.size);}&reduce=function(user_id,values_sizes){return Array.sum(values_sizes);}&collection=revisions" target="_blank">api/v1/mapreduce?map=function(){emit(this.user,this.size);}&reduce=function(user_id,values_sizes){ return Array.sum(values_sizes);}&collection=revisions</a></i>
    '''

    collection = request.args.get('collection', 'revisions')
    full_response = request.args.get('full_response', False)
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    query = request.get_json(silent=True)

    map_code = Code(request.args.get('map'))
    reduce_code = Code(request.args.get('reduce'))
    out = json_util.dumps({'out':'map_reduce'})

    result = db.mapreduce(out, collection, map_code, reduce_code, full_response, query)

    return Response(
        json_util.dumps(result.find()),
        mimetype='application/json'
    )

@api.route('/query', methods=['POST'])
@auto.doc()
def query():
    '''
    Use a json payload to query the collections using the mongoDB aggregate function

    Params:
    <ul class="params">
        <li>collection. Collection name. Defaults to 'revisions'</li>
        <li>date_format. Column date format. Defaults to %Y-%m-%dT%H:%M:%S</li>
        Example:
        URL: <a href="/api/v1/query?collection=revisions">/api/v1/query?collection=revisions</a>
        Payload: [{"$match": { "pageid": 630354 } }, { "$project" :{ "pageid": 1 , "revid" : 1 } }, { "$limit" : 5 } ]
    </ul>
    '''

    collection = request.args.get('collection', 'revisions')
    date_format = request.args.get('date_format', '%Y-%m-%dT%H:%M:%S')
    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})

    pipeline = request.get_json(silent=True)

    result = db.aggregate(collection, pipeline, date_format)
    return Response(
        json_util.dumps(result),
        mimetype='application/json'
    )


@api.route('/count', methods=['GET'])
@auto.doc()
def count():
    '''
    Returns the amount of revisions that match the criteria.

    Filters:
    <ul class="params">
        <li>title. The name of the wiki article of the revisions</li>
        <li>pageid. The id of the wiki article of the revisions</li>
        <li>user. The name of the Author of the revisions</li>
        <li>userid. The id of the Author of the revisions</li>
        <li>tag. A given tag of the revision</li>
        <li>size. The size of the revision</li>
        <li>sizematch. Used with size filtering to match revisions greater, lesser or with the exact size as given</li>
        <li>date. A given date for match revisions made that date</li>
        <li>datestart. Format: YYYY-MM-DD. Date from which will match the revisions If there is not dateend as arg, dateend would be consider the current date</li>
        <li>dateend. Format: YYYY-MM-DD. Date until which will match the revisions. If there is not datestart as arg, datestart would be consider the date of the first revision entered</li>
        <i>Example: <a href="count?datestart=2010-05-01&dateend=2010-06-01" target="_blank">/api/v1/count?datestart=2010-05-01&dateend=2010-06-01</a></i>
    </ul>
    '''

    arguments=filter_params(request)
    error_message=conditions_query(arguments)
    if error_message != None:
        return bad_request(error_message)

    #call the task with celery, passing the code to filter by attribute and the list of values(used by get_count)
    task= count_task.delay(arguments)
    result=task.get()
    if 'count' in result:
        return jsonify({'count':result['count']}), 200
    else:
        return bad_request("There was an error with the arguments, please check the query.")

@api.route('/avg', methods=['GET'])
@auto.doc()
def avg():
    '''Execute the average query

    Returns the average of revisions created between 2 dates.

    Filters:
    <ul class="params">
        <li>title. The name of the wiki article of the revisions</li>
        <li>pageid. The id of the wiki article of the revisions</li>
        <li>user. The name of the Author of the revisions</li>
        <li>userid. The id of the Author of the revisions</li>
        <li>tag. A given tag of the revision</li>
        <li>size. The size of the revision</li>
        <li>sizematch: Used with size filtering, to match the revisions greater, lesser or exact size as given</li>
        <li><strong>datestart. Required.</strong> Initial date of the interval from which will match the revisions. Date format: YYYY-MM-DD</li>
        <li><strong>dateend. Required.</strong> Final date of the interval until which will match the revisions. Date format: YYYY-MM-DD</li>
        <i>Example: <a href="avg?datestart=2010-05-01&dateend=2010-06-01" target="_blank">/api/v1/avg?datestart=2010-05-01&dateend=2010-06-01</a></i>
    </ul>
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
        return jsonify({'avg':result['avg']}), 200
    else:
        return bad_request("There was an error with the arguments, please check the query.")

@api.route('/mode', methods=['GET'])
@auto.doc()
def mode():
    '''
    Returns the value or values of most repetitions from the revisions, given an attribute.

    Params:
    <ul class="params">
        <li><strong>attribute. Required.</strong> Collection attribute to analize</li>
        Values:
        <ul class="params">
            <li>title. The name of the wiki article with most revisions</li>
            <li>pageid. The id of the wiki article with most revisions</li>
            <li>user. The name of the Author(s) which wrote most revisions</li>
            <li>userid. The id of the Author(s) which wrote most revisions</li>
            <li>size. The size of revision(s) most repeated</li>
            <li>date. The date on which most revisions were written</li>
        </ul>
        Filters. <strong>At least one attribute most be specified</strong>:
        <ul class="params">
            <li>title</li>
            <li>pageid</li>
            <li>user</li>
            <li>userid</li>
            <li>size</li>
            <li>sizematch</li>
            <li>date</li>
            <li>datestart</li>
            <li>dateend</li>
            <i>Avoid use unique date filter when using date as mode attribute, because it will return as best scenario the same date(in that case it is better to use a date interval)</i>
        </ul>
    </ul>
    <i>Example: <a href="mode?datestart=2010-01-01&attribute=user" target="_blank">/api/v1/mode?datestart=2010-01-01&attribute=user</a></i>
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
        return jsonify({mode_attribute:result['result']}), 200
    else:
        return bad_request("There was an error with the arguments, please check the query.")
