import requests
import time
from datetime import datetime

class RevisionExtractor(object):

    def __init__(self, payload={}, url='https://en.wikipedia.org/w/api.php', wait_time=2, db=None):
        self.payload = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'rvlimit': '100',
            'rvprop': 'ids|flags|timestamp|user|userid|size|sha1|contentmodel|comment|parsedcomment|content|tags',
            'rvdir':'newer',
        }
        self.payload.update(payload)

        self.url = url
        self.wait_time = wait_time
        self.db = db
        self.revendid=0


    def get_article(self):
        payload = {
            'action': 'query',
            'format': 'json',
            'titles': self.payload["titles"]
        }

        r = requests.get(self.url, params=payload)
        if r.status_code == requests.codes.ok:
            response = r.json()

            # Next Key its the id of the wiki.
            # Get json key an use it to access the revisions
            data = list(response["query"]["pages"])
            article = response["query"]["pages"][data[0]]
            if self.db.db.articles.find({'pageid': article["pageid"]}).count(True) == 0:
                # save data to db

                article["first_extraction_date"] = datetime.now()
                article["last_extraction_date"] = datetime.now()
                article["last_revision_extracted"]= self.find_last_revid()
                return self.db.db.articles.insert(article)
            else:
                article["last_extraction_date"] = datetime.now()
                article["last_revision_extracted"]= self.find_last_revid()
                self.db.db.articles.update({'pageid': article["pageid"]}, {"$set": article}, upsert=False)
        else:
            return r.raise_for_status()


    def get_all(self, celery_status=None):

        # Get the last revision extracted allocated in the DB
        self.revendid = self.find_last_revid()

        if self.revendid != 0:
            self.payload.update({'rvstartid': self.revendid})

        total_revisions = 0

        batch = self.get_one()

        if batch == False:
            return total_revisions
        else:
            # Count revisions extracted
            ks = list(batch["query"]["pages"])
            revision_count = len(batch["query"]["pages"][ks[0]]["revisions"])
            total_revisions += revision_count
            

        while ("continue" in batch):
            time.sleep(self.wait_time)
            self.payload.update({'rvcontinue': batch["continue"]["rvcontinue"]})
            batch = self.get_one()

            if celery_status != None:
                if batch == False:
                    return total_revisions

                # Count revisions extracted
                ks = list(batch["query"]["pages"])
                revision_count = len(batch["query"]["pages"][ks[0]]["revisions"])
                total_revisions += revision_count

                # Update status
                celery_status.update_state(state='IN PROGRESS', meta={
                                           'status': "%d revisions extracted" % (total_revisions)})
        self.get_article()
        return total_revisions

    def get_one(self):
        if self.url != None:
            r = requests.get(self.url, params=self.payload)
            if r.status_code == requests.codes.ok:
                response = r.json()
                # Next Key its the id of the wiki.
                # Get json key an use it to access the revisions
                ks = list(response["query"]["pages"])
                # save data to db
                data = response["query"]["pages"][ks[0]]["revisions"]
                article = {
                    'pageid': response["query"]["pages"][ks[0]]["pageid"],
                    'title': response["query"]["pages"][ks[0]]["title"],
                }
                if self.save(data, article) == False:
                    return False

                return response
            else:
                return r.raise_for_status()

    def save(self, revisions, article):
        return self.db.insert(revisions, self.revendid, article)

    def remove_all(self):
        self.db.remove()

    def find_last_revid(self):
        revision = self.db.find_last()
        if revision != None:
            revid = 0
            for rev in revision:
                revid = rev['revid']
        else:
            revid = 0
        return revid


#extractor = RevisionExtractor(payload={'titles': "Malazan Book of the Fallen"})
#content = extractor.get_all()
