from pymongo import MongoClient
import json
import datetime

class RevisionDB(object):
    
    config = {'host': 'localhost', 'port': 27017, 'username': '', 'password': ''}
    db = None
    client = None
    per_page = 20

    def __init__(self, config=None):
        if config == None:
            config = self.config

        self.client = MongoClient(host=config['host'],port=config['port'],connect=False)

        if self.client.wiki_history_extractor.authenticate(config['username'], config['password']) == True :
            self.db = self.client.wiki_history_extractor

    def insert(self, revisions, last_revision):
        #Insert only if it does not exists
        for revision in revisions:
            revision["formatted"] = False
            self.db.revisions.update({'revid': revision['revid']}, revision, upsert=True)
            #if revision['revid'] == last_revision:
                #return False
        return True

    #test method for inserting formatted timestamps
    def insert_date(self):
        self.db.revisions.insert({'id': 123,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,1,1,6,1,18)})
        self.db.revisions.insert({'id': 124,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,2,4,3,1,20)})
        self.db.revisions.insert({'id': 125,'user':'marvin','size':25980,'timestamp': datetime.datetime(2015,6,6,14,1,18)})

    def find(self):
        revisions = self.db.revisions.find()
        return revisions

    def find_query(self,query):
        revisions = self.db.revisions.find({},query)
        return revisions

    def count(self,query):
        revisions = self.db.revisions.find(query).count()
        return revisions

    def find_last(self):
        cursor= self.db.revisions.find({},{'revid':1 , '_id':0})
        cursor = cursor.sort('revid', -1).limit(1)
        return cursor

    def remove(self):
        revisions = self.db.revisions.remove({})
        return revisions

    def paginate(self, page):
        revisions = self.db.revisions.find().skip((page-1)*self.per_page).limit(self.per_page)
        return revisions


