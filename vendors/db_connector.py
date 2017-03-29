from pymongo import MongoClient
import json
import datetime

class RevisionDB(object):
    
    # it is extracted the information of the database connection, located in the 'connection_data.json' file
    with open('connection_data.json') as json_data:
        data = json.load(json_data)

    host=data['host']
    port=data['port']
    username=data['username']
    password=data['password']
    client = MongoClient(host=host,port=port)
    if client.wiki_history_extractor.authenticate(username, password, mechanism='SCRAM-SHA-1') == True :
        db = client.wiki_history_extractor

    @classmethod
    def insert(cls, revisions):
        #Insert only if it does not exists
        for revision in revisions:
            cls.db.revisions.update({'revid': revision['revid']}, revision, upsert=True)
            
    @classmethod
    #test method for inserting formatted timestamps
    def insert_date(cls):
        cls.db.revisions.insert({'id': 123,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,1,1,6,1,18)})
        cls.db.revisions.insert({'id': 124,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,2,4,3,1,20)})
        cls.db.revisions.insert({'id': 125,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,6,6,14,1,18)})

    @classmethod
    def find(cls):
        revisions = cls.db.revisions.find()
        return revisions

    @classmethod
    def find_query(cls,query):
        revisions = cls.db.revisions.find({},query)
        return revisions

    @classmethod
    def count(cls,query):
        revisions = cls.db.revisions.find(query).count()
        return revisions

    @classmethod
    def find_last(cls):
        cursor= cls.db.revisions.find({},{'revid':1 , '_id':0})
        cursor = cursor.sort('revid', -1).limit(1)
        return cursor

    @classmethod
    def remove(cls):
        revisions = cls.db.revisions.remove({})
        return revisions

