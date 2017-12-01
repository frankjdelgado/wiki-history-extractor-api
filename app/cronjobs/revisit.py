from datetime import datetime, date, time
import time
from math import factorial, exp
from config import config, Config
from vendors.db_connector import RevisionDB
from app.tasks.app_tasks import extract_article
import os

env_name = os.getenv('FLASK_CONFIG') or 'default'


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

# TODO: get proper probability distribution to calculat if an article should be revisited
def calculate_v2(last_date,nth_date,amount_revisions):

	#Lambda its calculated using the formula: Lambda= n / (t1 -t0)
	seconds=(last_date - nth_date).total_seconds() + 1

	lambda_exp= amount_revisions / (seconds*1.0)

	#Expected value ( E(x) = 1 /Lambda) is calculated
	expected_value= 1/(lambda_exp*1.0)
	#print expected_value

	#we get the time that has passed between the current time and the date of last revision
	time_since_last_revision= 	(datetime.now()-last_date).total_seconds() + 1
	#print time_since_last_revision

	#if the time that has passed between the current time and the date of last revision is greater than the expected value
	#the article shold be revisited
	if time_since_last_revision > expected_value:
		#print 'True'
		return True
	else:
		#print 'False'
		return False

def poisson(k, mean):
	# Formula: e**(-mean) * (mean**k / factorial(k))

	# e = eulers number
	# k = number of times an event occurs in an interval
	# mean = average number of events per interval
	return exp(-mean) * mean**k / factorial(k)


def binomial(n,x, p, q):
	return 	p**x * q**(n-x) * factorial(n) / (factorial(x) * factorial(n-x))
	

# Yearly avg amoung of revisions per article
def query_avg(db, pageid):
	pipe = [
		{'$match': {'pageid': pageid} },
		{'$project': { 'formattedDate': {'$dateToString': {'format': "%Y", 'date': "$timestamp"}} } },
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

# Loop through every article
# check if a article needs to be revisited
# extract data. add it to celery queue
def check_revisions(connection):

	# get total amount of articles
	#n_articles = len(db.articles())
	n_articles = connection.db.articles.count()
	#n_articles = connection.db
	# get cunks of 100 items per query
	per_page = 100

	# total amoint of iterations
	total = 1 + n_articles/per_page

	for page in xrange(1, total+1):

		# Get last revision of every article. Paginate on chunks of 100
		pipe = [
			{'$group':{'_id': "$title", 'date': { '$max': "$timestamp" }}},
			{'$skip': (page-1)*per_page},
			{'$limit': per_page},
		]
		cursor = connection.db.revisions.aggregate(pipeline=pipe)
		for document in cursor: 
		 	
		 	# Set revision date to YYYY-MM-DD 00:00:00
			#date = document['date'].replace(hour=0, minute=0, second=0)
			date = document['date']
			
			# Convert to integer
			#date_integer = int(time.mktime(date.timetuple()))

			#get total number of revisions for an article
			total_revisions= connection.db.revisions.find({'title':document['_id']}).count()

			#get 10% of total_revisions or 20, whichever is greater
			if total_revisions < 20:
				amount_revisions= total_revisions
			else:
				amount_revisions=int(max(20,total_revisions*0.1))

			#take the date of the nth revision, base of the amount_revisions, to calculate how much time has passed
			nth_date=db.get_nth_revision_date(title=document['_id'],n=amount_revisions)
			#nth_date_integer= int(time.mktime(nth_date.timetuple()))

			# Verify if article should be revisited
			should_revisit = calculate_v2(date,nth_date,amount_revisions)
			
			if should_revisit:
				# Revisit article. Extract revisions. Add to celery queue
				extract_article.delay(document['_id'])

db = RevisionDB(config={'host': config[env_name].MONGO_HOST, 'port': config[env_name].MONGO_PORT, 'username': config[env_name].MONGO_USERNAME, 'password': config[env_name].MONGO_PASSWORD})
# Run algorithm
check_revisions(db)
#print config
#date1=datetime(2015, 7, 14, 12, 30)
#date2=datetime(2017, 7, 14, 12, 30)
#calculate_v2(date2,date1,9)
 
#Lambda= 350.88
#E(x) = 0,002849977
