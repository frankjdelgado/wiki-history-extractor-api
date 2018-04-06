# wiki-history-extractor-api

A custom API to extract and display wikipedia article revisions. Provide custom metrics

### Recommended Requirements

* Python 2.7.10
* Mongo DB 3.2.12 
* RabbitMQ 3.5.4
* PyMongo 3.4.0 `pip install 'pymongo==3.4.0'`
* Flower 0.9.1 `pip install 'flower==0.9.1'`
* Celery 4.0.2 `pip install 'celery==4.0.2'`

### Development

#### Single Machine

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

* Install/Update Packages `./run.sh update`
* Start Server `./run.sh server`
* Start Celery `./run.sh celery`
* Create a mongo user.  Example:
	* Using the terminal, type: `mongo`
    * Once inside the mongo shell enter the following:
	
		`use wiki_history_extractor`
	
		`db.createUser({user: "wiki",pwd: "wiki123",roles: [{ role: "readWrite", db: "wiki_history_extractor" }]})`

#### Multiple Nodes
* This Docker setup will deplay the following services:
	* 3 Flask instances using nginx as a server and uwsgi as middleware
	* 1 Mongo instance (TODO: mongo replicas and shards)
	* 1 RabbitMQ instance (TODO: rabbitmq cluster)
	* 1 Nginx Load Balancer

* Install Docker. For detailed instructions please follow this [link](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository):
	* `sudo apt-get remove docker docker-engine docker.io`
	* `sudo apt-get update`
	* `sudo apt-get install \
		apt-transport-https \
		ca-certificates \
		curl \
		software-properties-common`
    * `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -`
    * `sudo add-apt-repository \
		"deb [arch=amd64] https://download.docker.com/linux/ubuntu \
		$(lsb_release -cs) \
		stable"`
	* `sudo apt-get update`
	* `sudo apt-get install docker-ce` 
	* `sudo groupadd docker` 
	* `sudo usermod -aG docker $USER`
	* `sudo -i`
	* ```curl -L https://github.com/docker/compose/releases/download/1.16.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose```
	* `sudo chmod +x /usr/local/bin/docker-compose`
	
* Run Servers
	* Generate `docker-compose.yml` file: `cp docker-compose.development.yml docker-compose.yml`
		* Use `docker-compose.replicas.yml` if you want to use a mongodb service with replicas and shards
	* `docker-compose up --scale worker=2`
		* You can setup `worker` with the number of containers that you like if you want more than one background worker. Ignore the worker parameter if you just need one worker
		* If using you are using `docker-compose.replicas.yml`, run `environments/mongo/init_docker.sh`
	* run `./environments/mongo/create_user.sh` the first time you run the app.
	* Go to `localhost/api/v1/`

### Endpoints

##### Docs

* `/api/v1/`

##### Extraction

* URL: `/api/v1/extract`
* params:
	* `title`: Wikipedia article title
* example:
	* `/api/v1/extract?title=Malazan Book of the Fallen`

### Monitoring

* Start Monitor `./run.sh monitor`
* Start Console Monitor `./run.sh events`


### Cronjobs

* enter `crontab -e`
* add line: `0 0 * * * (cd PATH/TO/PROJECT/ROOT/FOLDER/ && python -m app.cronjobs.revisit)`
