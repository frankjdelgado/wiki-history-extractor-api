from pymongo import MongoClient
import json
from datetime import datetime
from bson.objectid import ObjectId

class RevisionDB(object):
    
    default_config = {'host': 'localhost', 'port': 27017, 'username': '', 'password': ''}
    db = None
    client = None
    per_page = 20

    def __init__(self, config=None):
        if config == None:
            config = self.default_config
            
        self.client = MongoClient(config['host'],int(config['port']),connect=False)
        
        if self.client.wiki_history_extractor.authenticate(config['username'], config['password']) == True :
            self.db = self.client.wiki_history_extractor

    def db():
        return self.db

    def revisions(self, query={}, page=None, per_page=None, sort=1):
        
        for term in query:
            if term == "_id":
                query[term] = ObjectId(query[term]) 

        if sort == 'asc':
            sort = 1
        elif sort == 'desc':
            sort = -1


        if page==None or per_page==None:
            return self.db.revisions.find(query).sort('timestamp', sort)
        else:
            return self.db.revisions.find(query).skip((page-1)*per_page).limit(per_page).sort('timestamp', sort)
    
    def articles(self, query={}, page=None, per_page=None):
        for term in query:
            if term == "_id":
                query[term] = ObjectId(query[term]) 

        if page==None or per_page==None:
            return self.db.articles.find(query)
        else:
            return self.db.articles.find(query).skip((page-1)*per_page).limit(per_page)

    def article(self,query={}):
        return self.db.articles.find_one(query)
        
    def last_revs(self):
        cursor= self.db.articles.find({},{'last_extraction_date':1 ,'pageid':1, '_id':0})
        cursor=list(cursor)
        return cursor


    def insert(self, revisions, last_revision, article):
        #Insert only if it does not exists
        for revision in revisions:

            #Format adata
            revision = self.format_raw_revision(revision, article)

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

    def find_query(self,filters,query):
        if filters=='' or filters==None:
            revisions = self.db.revisions.find({},query)
        else:
            revisions = self.db.revisions.find(filters,query)
        return revisions

    def count(self,query):
        revisions = self.db.revisions.find(query).count()
        return revisions

    def filter_query(self,query):
        revisions = self.db.revisions.find(query)
        return revisions

    def find_last(self,pageid):
        cursor= self.db.revisions.find({'pageid':pageid},{'revid':1 , '_id':0})
        cursor = cursor.sort('revid', -1).limit(1)
        return cursor

    def remove(self):
        revisions = self.db.revisions.remove({})
        return revisions

    def paginate(self, query={}, page=1,per_page=20):
        if page < 1:
            page = 1
        if page_size > 250:
            page_size = 250

        revisions = self.db.revisions.find(query).skip((page-1)*per_page).limit(per_page)
        return revisions

    def paginate_for_query(self, filters, projection,page, per_page=20):
        revisions = self.db.revisions.find(filters,projection).skip((page-1)*per_page).limit(per_page)
        return revisions

    def update(self, filter, new_data):
        revisions = self.db.revisions.update(filter, new_data, upsert=False)
        return revisions

    def format_raw_revision(self, revision, article):
        revision["timestamp"] = datetime.strptime(revision["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
        revision["extraction_date"] =  datetime.now()
        revision["pageid"] = article["pageid"]
        revision["title"] = article["title"]
        return revision


