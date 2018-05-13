# wiki-history-extractor-api

A custom API to extract and display wikipedia article revisions. Provide custom metrics

## Recommended Requirements

* Python 2.7.10
* MongoDB 3.4.7
* PyMongo 3.4.0

## Development

### Single Machine

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
    ```javascript
    use wiki_history_extractor;

    db.createUser({user: "wiki",pwd: "wiki123",roles: [{ role:    "readWrite", db: "wiki_history_extractor" }]});
    ```

### Docker Deployment

* For deployment at the UCV labs you will first need to use a VPN

  * Download `<ovpn_file_name>.ovpn`

  * Import the certifcate (double click) `<certificate_name>.crt`

  * `sudo apt-get install openvpn easy-rsa`

  * Start openvpn `sudo openvpn --config <ovpn_file_name>.ovpn`

  * Open a new terminal and connect to the server `ssh <user>@<ip>`

* Install Docker. For detailed instructions please follow this [link](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository):

  * `sudo apt-get remove docker docker-engine docker.io`

  * `sudo apt-get update`

  * ```
    sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
    ```

  * `curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -`

  * ```
    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"
    ```

  * `sudo apt-get update`

  * `sudo apt-get install docker-ce`

  * `sudo groupadd docker`

  * `sudo usermod -aG docker $USER`

  * `sudo -i`

  * `sudo curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
  `

  * `sudo chmod +x /usr/local/bin/docker-compose`

* Setup Docker Containers and Images

  * `cp docker-compose.production.yml docker-compose.yml`

  * `docker-compose build`

  * Cluster:

    * `docker-compose up -d --scale flask=3 worker=3`

    * `./docker/mongo/setup_nodes.sh`

  * Single Node:

    * `docker-compose up -d` for Development

    * `./docker/mongo/create_user.sh`

  * Check the logs using `docker-compose logs`

#### Routes

* Documentation: `/api/v1/`
* MongoDB web admin: `/adminmongo`
* Flower Monitor: `/flower`

User username `wiki` and password `wiki123`

### Tests

* Without Docker

  1. `. bin/activate`

  1. `FLASK_CONFIG=testing`

  1. `python -m app.tests.test_api`

* Docker: `./docker/tests/run.sh`

### Cronjobs

* enter `crontab -e`
* add line: `0 0 * * * (cd PATH/TO/PROJECT/ROOT/FOLDER/ && python -m app.cronjobs.revisit)`
