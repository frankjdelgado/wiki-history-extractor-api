from __future__ import absolute_import, unicode_literals
from .. import celery
from config import config, Config
from vendors.db_connector import RevisionDB
from vendors.query_handler import QueryHandler
from vendors.api_extractor import RevisionExtractor
import time


@celery.task(bind=True)
def hello(self):

    for x in xrange(1, 11):
        print "Hello World! %d" % x
        self.update_state(state='PROGRESS',
                          meta={'status': "Hello World Step %d / 10!" % x})
        time.sleep(2)

    return {'status': 'Task completed!',
            'result': "Hello World Step %d / 10" % x}


@celery.task(bind=True)
def extract_article(self, title, locale='en', pageid=None):

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})

    extractor = RevisionExtractor(payload={'titles': title}, title=title, db=db, locale=locale, pageid=pageid)
    total = extractor.get_all(self, locale=locale)

    return {'status': 'Task completed!',
            'result': "%d revisions extracted" % total}

@celery.task(bind=True)
def clean_revisions(self, title):

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})

    db.find_query({formatted: False})

    self.update_state(state='IN PROGRESS', meta={'status': "%d revisions extracted" % (2)})
    return {'status': 'Task completed!',
            'result': "%d revisions extracted" % total}
            
@celery.task(bind=True)
def count_task(self,arguments):

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    #instantiate a new QueryHandler to get execute the corresponding function
    handler = QueryHandler(db=db)
    number = handler.get_count(arguments)
    if number!=None:
        return {'status': 'Task completed!', 
                'count': "%d" % number}
    else:
        return {'status': 'Task failed!'}

@celery.task(bind=True)
def avg_task(self,values):

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    #instantiate a new QueryHandler to get execute the corresponding function
    handler = QueryHandler(db=db)
    number = handler.get_avg(values)
    if number!=None:
        return {'status': 'Task completed!', 
                'avg': "%f" % number}
    else:
        return {'status': 'Task failed!'}


@celery.task(bind=True)
def mode_task(self,values,mode_attribute):

    db = RevisionDB(config={'host': config['default'].MONGO_HOST, 'port': config['default'].MONGO_PORT, 'username': config['default'].MONGO_USERNAME, 'password': config['default'].MONGO_PASSWORD, 'db_name':config['default'].MONGO_DB_NAME})
    #instantiate a new QueryHandler to get execute the corresponding function
    handler = QueryHandler(db=db)
    number = handler.get_mode(values,mode_attribute)
    if number!=None:
        return {'status': 'Task completed!', 
        'result': "%s" % number}
    else:
        return {'status': 'Task failed!'}
