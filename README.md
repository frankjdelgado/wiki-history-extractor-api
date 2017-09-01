# wiki-history-extractor-api
API developed to get metrics of the history revisions of wiki articles.

### Recommended Requirements

* Python 2.7.10
* Mongo DB 3.2.12 
* RabbitMQ 3.5.4
* PyMongo 3.4.0 ```pip install 'pymongo==3.4.0'```
* Flower 0.9.1 ```pip install 'flower==0.9.1'```
* Celery 4.0.2 ```pip install 'celery==4.0.2'```

### Development
* We recommend the use of `virtualenv`
	* `pip install virtualenv`
	* `cd wiki-history-extractor-api`
	* `virtualenv .`
	* Use `. bin/activate` to be able activate the virtual environment in your current console window. For example:
		* First window:
			1. `. bin/activate`
			2. `./run.sh update`
			3. `./run.sh server`
		* Second window:
			1. `./run.sh celery`

* Install/Update Packages ```./run.sh update```
* Start Server ```./run.sh server```
* Start Celery ```./run.sh celery```
* Create a mongo user.  Example:
	* Using the terminal, type: ```mongo```
	* Once inside the mongo shell enter the following:
	
		```use wiki_history_extractor```
	
		```db.createUser({user: "wiki",pwd: "wiki123",roles: [{ role: "readWrite", db: "wiki_history_extractor" }]})```
	
### Endpoints

##### Docs

* ```/api/v1/```

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

* enter ```crontab -e```
* add line: ```0 0 * * * (cd PATH/TO/PROJECT/ROOT/FOLDER/ && python -m app.cronjobs.revisit)```
