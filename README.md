# wiki-history-extractor-api
API developed to get metrics of the history revisions of wiki articles.

### Requirements

* Python 2.7.10
* Mongo DB 3.2.12 
* RabbitMQ 3.5.4
* PyMongo 3.4.0 ```sudo pip install 'pymongo==3.4.0'```
* Flower 0.9.1 ```sudo pip install 'flower==0.9.1'```
* Celery 4.0.2 ```sudo pip install 'celery==4.0.2'```

### Development

* Start Server ```./run.sh server```
* Start Celery ```./run.sh celery```
* Install/Update Packages ```./run.sh update```
* Create a mongo user.  Example:
	* Using the terminal, type: ```mongo```
	* Once inside the mongo shell enter the following:
	
		```use wiki_history_extractor```
	
		```db.createUser({user: "wiki",pwd: "wiki123",roles: [{ role: "readWrite", db: "wiki_history_extractor" }]})```
	
		```exit```

### Endpoints

##### Extraction

* URL: ```/api/v1/extract```
* params:
	* ```title```: Wikipedia article title
* example:
	* ```/api/v1/extract?title=Malazan Book of the Fallen```

### Monitoring

* Start Monitor ```./run.sh monitor```
* Start Console Monitor ```./run.sh events```


### Cronjobs

* enter ``` sudo crontab -e```
* add line: ```0 0 * * * (cd PATH/TO/PROJECT/ROOT/FOLDER/ && python -m app.cronjobs.revisit)```
