FROM tiangolo/uwsgi-nginx-flask:python2.7

COPY /environments/development/celery/celery.conf /etc/supervisor/conf.d/celery.conf
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
