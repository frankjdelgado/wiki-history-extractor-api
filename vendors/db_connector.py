from pymongo import MongoClient
import json
from datetime import datetime
from bson.objectid import ObjectId
from config import config, Config
from vendors.query_handler import QueryHandler

class RevisionDB(object):
    default_config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME}   
    db = None
    client = None
    per_page = 20

    def __init__(self, config=None):
        if config == None:
            config = self.default_config
            
        self.client = MongoClient(config['host'],int(config['port']),connect=False)
        dbname=config['db_name']
#        print dbname
        if self.client[dbname].authenticate(config['username'], config['password']) == True :
            self.db = self.client[dbname]

    def db():
        return self.db

    def mapreduce(self, out, collection='revisions', map=None, reduce=None, full_response=False, query={} ):
        if collection == 'revisions':
            return self.db.revisions.map_reduce(map, reduce, out=out ,full_response=full_response, query=query)
        else:
            return self.db.articles.map_reduce(map, reduce, out=out, full_response=full_response, query=query)

    def aggregate(self, collection='revisions', pipeline=[], date_format='%Y-%m-%dT%H:%M:%S'):

        for item in pipeline:
            if "$match" in item:
                for column in ['timestamp','extraction_date','first_extraction_date','last_extraction_date']:
                    if column in item["$match"]:
                        for operator in ['$gte','$gt','$lt']:
                            if operator in item["$match"][column]:
                                item["$match"][column][operator] = datetime.strptime(item["$match"][column][operator],date_format)
                        if type(item["$match"][column]) is not dict:
                            item["$match"][column] = datetime.strptime(item["$match"][column],date_format)
  
        if collection == 'revisions':
            return self.db.revisions.aggregate(pipeline)
        else:
            return self.db.articles.aggregate(pipeline)


    def revisions(self, query={}, page=None, per_page=None, sort=1):
        query = QueryHandler(db=self.db).get_query(query)
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])

        if sort == 'asc':
            sort = 1
        elif sort == 'desc':
            sort = -1

        if page==None or per_page==None:
            revisions= self.db.revisions.find(query).sort('timestamp', sort)
        else:
            revisions= self.db.revisions.find(query).skip((page-1)*per_page).limit(per_page).sort('timestamp', sort)

        result=[]
        for rev in revisions:
            rev['timestamp']=rev['timestamp'].isoformat()
            rev['extraction_date']=rev['extraction_date'].isoformat()
            result.append(rev)
        return result
    
    def articles(self, query={}, page=None, per_page=None):
        query = QueryHandler(db=self.db).get_query(query)
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])

        if page==None or per_page==None:
            articles= self.db.articles.find(query)
        else:
            articles= self.db.articles.find(query).skip((page-1)*per_page).limit(per_page)

        result=[]
        for rev in articles:
            rev['first_extraction_date']= rev['first_extraction_date'].isoformat()
            rev['last_extraction_date']= rev['last_extraction_date'].isoformat()
            result.append(rev)

        return result

    def article(self,query={}):
        art=self.db.articles.find_one(query)
        art['first_extraction_date']= art['first_extraction_date'].isoformat()
        art['last_extraction_date']= art['last_extraction_date'].isoformat()
        return art
        
    def last_revs(self):
        cursor= self.db.articles.find({},{'last_extraction_date':1 ,'pageid':1, '_id':0})
        cursor=list(cursor)
        return cursor


    def insert(self, revisions, last_revision, article):
        #Insert only if it does not exists
        for revision in revisions:

            #Format adata
            revision = self.format_raw_revision(revision, article)
            revision['locale'] = article['locale']


            self.db.revisions.update({'revid': revision['revid']}, revision, upsert=True)
        return True

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

    def get_nth_revision_date(self,title,n,projection={'timestamp':1,'revid':1,'_id':0}):
        revisions = self.db.revisions.find({'title':title},projection).limit(n)
        revision = revisions.sort('timestamp', -1).limit(1)
        for rev in revision:
            return rev['timestamp']

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



