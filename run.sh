#!/bin/bash

install_requirements(){
	sudo pip install -r requirements.txt
}

run_server(){
	python manage.py runserver
}

run_celery(){
	celery worker -A celery_worker.celery --loglevel=info
}

do_nothing(){
	echo "Invalid arguments..."
}

option=$1

case $1 in
	"update")
		install_requirements
		;;
	"server")
		run_server
		;;
	"celery")
		run_celery
		;;
	*)
		do_nothing
esac

