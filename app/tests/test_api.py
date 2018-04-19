import unittest
from app import create_app
from vendors.api_extractor import RevisionExtractor
import requests
import json
import sys
import time
from pymongo import MongoClient
from config import config
from app.api_1_0 import api as api_1_0_blueprint

class TestWikiApi(unittest.TestCase):
    def setUp(self):
        client=MongoClient(config['testing'].MONGO_HOST, int(config['testing'].MONGO_PORT),connect=False)
        dbname=config['testing'].MONGO_DB_NAME
        users=client[dbname].command("usersInfo", "wiki")
        if users['users'][0]['user']=='wiki':
            client[dbname].command("dropUser", "wiki")

        client[dbname].command("createUser", "wiki", pwd="wiki123", roles=["readWrite"])

        app = create_app('testing')
        app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1')
        self.app= app.test_client()

#    def tearDown(self):
#        client=MongoClient(config['testing'].MONGO_HOST, int(config['testing'].MONGO_PORT),connect=False)
#        dbname=config['testing'].MONGO_DB_NAME
#
#        client[dbname].command("dropUser", "wiki")
#        client.drop_database(dbname)

    def test_data_extraction(self):
        response = self.app.get('/api/v1/extract?title=Dungeon_Siege')
        # the JSON object got as response is decoded with json.loads into a dictionary
        task_link = json.loads(response.get_data())
        #it is extracted the link of the task, to check its state with a new request
        location= task_link['Location']
        response_task_state = self.app.get(location)
        task_link = json.loads(response_task_state.get_data())
        #it is checked the state of the task until is completed
        while task_link['state'] =='PENDING' or task_link['state'] =='IN PROGRESS' :
            time.sleep(10)
            response_task_state = self.app.get(location)
            task_link = json.loads(response_task_state.get_data())

        #finally, the test is successful if the task complete with a state of SUCCESS
        self.assertEqual(task_link['state'], 'SUCCESS')

#    def test_status_code(self):
#        response = self.app.get('/api/v1/count?size=1&sizematch=greater&datestart=2000-01-01&dateend=2017-01-01&title=Warhammer 40,000 comics')
#        self.assertEqual(response.status_code, 200)

#    def test_data(self):
#        response = self.app.get('/api/v1/count?size=1&sizematch=greater&datestart=2000-01-01&dateend=2017-01-01&title=Warhammer 40,000 comics')
#        self.assertEqual(json.loads(response.get_data()), {'count': '0'})

    def test_endpoint_articles(self):
        response = self.app.get('/api/v1/articles')
        self.assertEqual(response.status_code, 200)        

    def test_endpoint_article(self):
        response = self.app.get('/api/v1/articles/630354')
        self.assertEqual(response.status_code, 200)        

    def test_endpoint_revisions(self):
        response = self.app.get('/api/v1/revisions')
        self.assertEqual(response.status_code, 200)

    #test revisions with sorting
    def test_endpoint_revisions_sorted(self):
        response = self.app.get('/api/v1/revisions?user=PresN&sort=asc')
        data=json.loads(response.get_data())
        self.assertEqual(int(data[0]['revid']), 115476135)

    #test revisions with pagination
    def test_endpoint_revisions_plus_paginated(self):
        response = self.app.get('/api/v1/revisions?user=PresN&sort=asc&page_size=5&page=2')
        data=json.loads(response.get_data())
        self.assertEqual(int(data[0]['revid']), 767697090)

    def test_endpoint_count(self):
        response = self.app.get('/api/v1/count?title=Dungeon Siege')
        self.assertEqual(response.status_code, 200)

    #test count with aditional date filter
    def test_endpoint_count_plus(self):
        response = self.app.get('/api/v1/count?title=Dungeon Siege&date=2004-06-22')
        data=json.loads(response.get_data())
        self.assertEqual(int(data['count']), 10)

    def test_endpoint_avg(self):
        response = self.app.get('/api/v1/avg?title=Dungeon Siege&datestart=2000-01-01&dateend=2010-01-01')
        self.assertEqual(response.status_code, 200)

    #test avg with aditional user filter
    def test_endpoint_avg_plus(self):
        response = self.app.get('/api/v1/avg?title=Dungeon Siege&datestart=2004-05-01&dateend=2004-05-10&user=Jahaza')
        data=json.loads(response.get_data())
        self.assertEqual(float(data['avg']), 0.2)

    def test_endpoint_mode(self):
        response = self.app.get('/api/v1/mode?title=Dungeon Siege&attribute=date')
        self.assertEqual(response.status_code, 200)

    #test mode with aditional user
    def test_endpoint_mode_plus(self):
        response = self.app.get('/api/v1/mode?title=Dungeon Siege&date=2018-02-19&attribute=user')
        data=json.loads(response.get_data())
        self.assertEqual(data['user'], "['Lordtobi']")

    def test_endpoint_query(self):
        payload= [{"$match": { "pageid": 630354}},{ "$project" :{ "pageid": 1 , "timestamp" : 1}},{ "$limit" : 5 },{"$sort":{"timestamp":1}}]
        response = self.app.post('/api/v1/query',data=json.dumps(payload),headers = {'content-type': 'application/json'})
        self.assertEqual(response.status_code, 200)

    def test_endpoint_mapreduce(self):
        code_map='function() { emit(this.user,this.size); }'
        code_reduce= 'function(user_id,values_sizes){ return Array.sum(values_sizes);}'
        payload={}
        response = self.app.post('/api/v1/mapreduce?map='+code_map+'&reduce='+code_reduce,data=json.dumps(payload),headers = {'content-type': 'application/json'})
        self.assertEqual(response.status_code, 200)




if __name__ == "__main__":
    unittest.main()