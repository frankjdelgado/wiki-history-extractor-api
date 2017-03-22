# wiki-history-extractor-api

### Requirements

* Python 2.7.10
* Mongo DB 3.2.12
* Celery 4.0.2
* RabbitMQ 3.5.4

### Development

* Start server ```./app.py```
* Start Celery ```celery -A vendors worker --loglevel=info```