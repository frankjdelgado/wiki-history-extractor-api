import requests
import time

class RevisionExtractor(object):

    def __init__(self, payload={}, url='https://en.wikipedia.org/w/api.php', wait_time=2, db=None):
        self.payload = {
            'action': 'query',
            'format': 'json',
            'prop': 'revisions',
            'rvlimit': '50',
            'rvprop': 'ids|flags|timestamp|user|flags|user|userid|size|sha1|contentmodel|comment|parsedcomment|content|tags',
        }
        self.payload.update(payload)

        self.url = url
        self.wait_time = wait_time
        self.db = db
        
        # Get the last revision extracted allocated in the DB
        self.revendid = self.find_last_revid()


    def get_all(self, celery_status=None):

        total_revisions = 0

        batch = self.get_one()

        if batch == False:
            return total_revisions

        while ("continue" in batch):
            time.sleep(self.wait_time)
            self.payload.update({'rvcontinue': batch["continue"]["rvcontinue"]})
            batch = self.get_one()

            if celery_status != None:
                if batch == False:
                    return total_revisions

                # Count revision extracted
                ks = list(batch["query"]["pages"])
                revision_count = len(batch["query"]["pages"][ks[0]]["revisions"])
                total_revisions += revision_count

                # Update status
                celery_status.update_state(state='PROGRESS', meta={
                                           'status': "%d revisions extracted" % (total_revisions)})

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
                if self.save(response["query"]["pages"][ks[0]]["revisions"]) == False:
                    return False

                return response
            else:
                return r.raise_for_status()

    def save(self, revisions):
        return self.db.insert(revisions, self.revendid)

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
