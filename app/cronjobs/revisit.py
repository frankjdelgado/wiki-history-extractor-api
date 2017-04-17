from datetime import datetime, date, time
import time
from math import factorial, exp
from config import config, Config
from vendors.db_connector import RevisionDB
from app.tasks.app_tasks import extract_article

# Based on wikimetrics ucv formula
# t0: last time the article was updated
# t1: current time
def calculate_v1(t0):
	ti = int(time.mktime(datetime.now().timetuple()))
	
	result = 1 - (t0/ti)

	if result > 0:
		return True
	else:
		return False

def calculate_v2(k=1,mean=1):
	result = poisson(k, mean)

	if result > 0.5:
		return True
	else:
		return False
	
	return true

def poisson(k, mean):
	# Formula: e**(-mean) * (mean**k / factorial(k))

	# e = eulers number
	# k = number of times an event occurs in an interval
	# mean = average number of events per interval
	return exp(-mean) * mean**k / factorial(k)


def binomial(n,x, p, q):
	return 	p**x * q**(n-x) * factorial(n) / (factorial(x) * factorial(n-x))
	

def query_avg(db, pageid):
	pipe = [
		{'$match': {'pageid': pageid} },
		{'$project': { 'formattedDate': {'$dateToString': {'format': "%Y-%m", 'date': "$timestamp"}} } },
		{'$group': { '_id': "$formattedDate", 'total_revisions': {'$sum': 1}} },
		{'$group': {'_id': "1", 'avg_count': { '$avg':"$total_revisions" }}}
	]

	cursor = db.revisions().aggregate(pipeline=pipe)
	result = None
	
	for document in cursor: 
		result = document
	
	if result != None:
		result = result['avg_count']

	return result

def last_revision(pageid):

	pipe = [
		{'$match': { 'pageid': pageid }},
		{'$project': { 'formattedDate': {'$dateToString': {'format': "%Y-%m-%d", 'date': "$timestamp"}} } },
		{'$group':{'_id': "$pageid", 'date': { '$max': "$formattedDate" }}}
	]

	cursor = db.revisions().aggregate(pipeline=pipe)
	result = None
	
	for document in cursor: 
		result = document
	
	if result != None:
		result = result['date']

	return result

def check_revisions(db):

	n_articles = db.articles().count()
	per_page = 100

	
	for page in xrange(1, n_articles):

		pipe = [
			{'$group':{'_id': "$title", 'date': { '$max': "$timestamp" }}},
			{'$skip': (page-1)*per_page},
			{'$limit': per_page},
		]
		cursor = db.revisions().aggregate(pipeline=pipe)
		for document in cursor: 
		 	
			date = document['date'].replace(hour=0, minute=0, second=0)
			date_integer = int(time.mktime(date.timetuple()))

			should_revisit = calculate_v1(date_integer)
			
			if should_revisit:
				extract_article.delay(document['_id'])

db = RevisionDB(config={'host': Config.MONGO_HOST, 'port': Config.MONGO_PORT, 'username': Config.MONGO_USERNAME, 'password': Config.MONGO_PASSWORD})

check_revisions(db)

 
