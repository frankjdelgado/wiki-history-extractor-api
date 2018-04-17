FROM python:2.7-alpine

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    linux-headers
    
RUN pip install uwsgi

COPY requirements.txt /tmp/
WORKDIR /tmp
RUN pip install -r requirements.txt

RUN mkdir /app
WORKDIR /app
ADD . /app

ENV PYTHONPATH=/app
RUN addgroup -S uwsgi
RUN adduser -S -g uwsgi uwsgi

#CMD python manage.py runserver --host 0.0.0.0 --port=80