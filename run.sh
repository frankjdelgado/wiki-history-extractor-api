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

run_monitor(){
	celery flower -A celery_worker.celery --loglevel=info
}

run_events(){
	celery events -A celery_worker.celery --loglevel=info
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
	"monitor")
		run_monitor
		;;
	"events")
		run_events
		;;
	*)
		do_nothing
esac

