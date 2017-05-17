from flask import Flask, request, jsonify, Response, url_for
import urlparse
from bson import json_util
from .errors import bad_request 
from . import api,auto
from app.tasks.app_tasks import count_task, avg_task, mode_task


@api.route('/count', methods=['GET'])
@auto.doc()
def count():
    '''The function execute the count query, which returns the amount of revisions which match the criteria. The function can receive several parameters to filtering the results: user: the name of the Author of the revisions. tag: a given tag of the revision. size: the size of the revision. sizematch: Used with size filtering, to match the revisions greater, lesser or exact size as given. (Dates will be in format YYYY-MM-DD) date: a given date for match revisions made that date. datestart: date from which will match the revisions. If there is not dateend as arg, dateend would be consider the current date. dateend: date until which will match the revisions. If there is not datestart as arg, datestart would be consider the date of the first revision entered.'''
    code=0
    values=[]
    if request.args.get('user') != None:
        user = request.args.get('user')
        #adds the value to the values list
        values.append(user)
        code= code + 1000
    if request.args.get('tag') != None:
        tag = request.args.get('tag')
        #adds the value to the values list
        values.append(tag)
        code= code + 100
    if request.args.get('size') != None and request.args.get('sizematch') != None:
        size = int(request.args.get('size'))
        if size<0:
            return bad_request("Error with the arguments, please check the query.") 
        sizematch= request.args.get('sizematch')
        #adds the values to the values list
        values.append(size)
        if sizematch == "greater":
            values.append(1)
        elif sizematch == "lesser":
            values.append(-1)
        elif sizematch == "equal":
            values.append(0)
        else:
            return bad_request("Error with the arguments, please check the query.") 
        code= code + 10

    date = request.args.get('date')
    datestart = request.args.get('datestart')
    dateend = request.args.get('dateend')
    if date != None or datestart != None or dateend != None:
        #in case of exact date, datestart and dateend must not be in the query
        if date != None and datestart == None and dateend == None:
            values.append(date)
        #in case of a date interval, date must not be in the query
        elif date == None:
            #adds the value to the values list
            if dateend == None:
                values.append(datestart)
                values.append(1)
            elif datestart == None:
                values.append(dateend)
                values.append(-1)
            else:
                values.append(datestart)
                values.append(dateend)
        else:
            return bad_request("Error with the arguments, please check the query.")
        code= code + 1
    if code==0:
        return bad_request("Must add some arguments, please check the query.")
    #call the task with celery, passing the code to filter by attribute and the list of values(used by get_count)
    task= count_task.delay(code,values)
    result=task.get()
    return jsonify({'count':result['count']}), 202


@api.route('/avg', methods=['GET'])
@auto.doc()
def avg():
    '''The function execute the average query, which returns the average of revisions which match the criteria between 2 dates. The function can receive ONE CRITERIA to filtering the results, besides the dates of the interval: user: the name of the Author of the revisions. tag: a given tag of the revision. size: the size of the revision. sizematch: Used with size filtering, to match the revisions greater, lesser or exact size as given. (Dates will be in format YYYY-MM-DD) datestart: initial date of the interval from which will match the revisions. dateend: final date of the interval until which will match the revisions.'''
    code=0
    values=[]
    if request.args.get('user') != None:
        user = request.args.get('user')
        values.append(user)
        code= 1
    elif request.args.get('tag') != None:
        tag = request.args.get('tag')
        values.append(tag)
        code= 2
    elif request.args.get('size') != None and request.args.get('sizematch') != None:
        size = int(request.args.get('size'))
        if size<0:
            return bad_request("Error with the arguments, please check the query.") 
        sizematch= request.args.get('sizematch')
        values.append(size)
        if sizematch == "greater":
            values.append(1)
        elif sizematch == "lesser":
            values.append(-1)
        elif sizematch == "equal":
            values.append(0)
        else:
            return bad_request("Error with the arguments, please check the query.") 
        code= 3
    else:
        return bad_request("Must add some arguments, please check the query.") 

    datestart = request.args.get('datestart')
    dateend = request.args.get('dateend')
    if datestart != None and dateend != None:
        values.append(datestart)
        values.append(dateend)
    else:
        return bad_request("Error with the arguments, please check the query.")

    task= avg_task.delay(code,values)
    result=task.get()
    return jsonify({'avg':result['avg']}), 202


@api.route('/mode', methods=['GET'])
@auto.doc()
def mode():
    '''The function execute the mode query, which returns the amount of criteria of most repetitions from the revisions. The function receive ONE CRITERIA, using the 'attribute' key, and one of the following values: user: the name of the Author(s) which wrote most revisions. size: the size of revision(s) most repeated. date: the date on which most revisions were written. For now, mode for tag criteria is disabled, due to lack of tags in revisions. It can ALSO receive '''
    values=[]
    code=0
    if request.args.get('user') != None:
        user = request.args.get('user')
        values.append(user)
        code= code + 1000
#    if request.args.get('tag') != None:
#        tag = request.args.get('tag')
#        values.append(tag)
#        code= code + 100
    if request.args.get('size') != None and request.args.get('sizematch') != None:
        size = int(request.args.get('size'))
        if size<0:
            return bad_request("Error with the arguments, please check the query.") 
        sizematch= request.args.get('sizematch')
        values.append(size)
        if sizematch == "greater":
            values.append(1)
        elif sizematch == "lesser":
            values.append(-1)
        elif sizematch == "equal":
            values.append(0)
        else:
            return bad_request("Error with the arguments, please check the query.") 
        code= code + 10

    date = request.args.get('date')
    datestart = request.args.get('datestart')
    dateend = request.args.get('dateend')
    if date != None or datestart != None or dateend != None:
        #in case of exact date, datestart and dateend must not be in the query
        if date != None and datestart == None and dateend == None:
            values.append(date)
        #in case of a date interval, date must not be in the query
        elif date == None:
            if dateend == None:
                values.append(datestart)
                values.append(1)
            elif datestart == None:
                values.append(dateend)
                values.append(-1)
            else:
                values.append(datestart)
                values.append(dateend)
        else:
            return bad_request("Error with the arguments, please check the query.")
        code= code + 1

    attribute = request.args.get('attribute')
    if attribute != None:
        if attribute == 'user':
            task= mode_task.delay(1,code,values)
            result=task.get()
            return jsonify({'user':result['result']}), 202
        elif attribute == 'size':
            task= mode_task.delay(2,code,values)
            result=task.get()
            return jsonify({'size':result['result']}), 202
#        elif attribute == 'tag':
#            task= mode_task.delay(3,code,values)
#            result=task.get()
#            return jsonify({'tag':result['result']}), 202
        elif attribute == 'date':
            task= mode_task.delay(4,code,values)
            result=task.get()
            return jsonify({'date':result['result']}), 202
        else:
            return bad_request("Error with the arguments, please check the query.")
    else:
        return bad_request("Must add some arguments, please check the query.")
            

