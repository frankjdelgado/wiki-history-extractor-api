from __future__ import absolute_import, unicode_literals
from .. import celery
import time
from vendors.api_extractor import RevisionExtractor
from vendors.db_connector import RevisionDB


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
def extract(self, title):

    extractor = RevisionExtractor(payload={'titles': title})
    total = extractor.get_all(self)

    return {'status': 'Task completed!',
            'result': "%d revisions extracted" % total}
