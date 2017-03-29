# wiki-history-extractor-api

### Requirements

* Python 2.7.10
* Mongo DB 3.2.12
* Celery 4.0.2
* RabbitMQ 3.5.4

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
