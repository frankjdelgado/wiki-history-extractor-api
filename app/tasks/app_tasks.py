from __future__ import absolute_import, unicode_literals
from . import celery

# Get status using self
@celery.task(bind=True)
def hello(self):

	for x in xrange(1,10):
		print "Hello World!"
		self.update_state(state='PROGRESS',
                          meta={'current': x, 'total': 10,
                                'status': "Hello World Step %d / 10!" % x})
        time.sleep(1)

	return {'current': 10, 'total': 10, 'status': 'Task completed!',
            'result': "Hello World Step %d / 10"%x}