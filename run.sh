#!/bin/bash

install_requirements(){
	echo "Install Requirements"
	pip install -r requirements.txt
}

run_server(){
	echo "Start Python Dev Server"
	python manage.py runserver
}

run_celery(){
	echo "Start Celery Workers"
	celery worker -A celery_worker.celery --loglevel=info
}

run_monitor(){
	echo "Start Flower Monitor"
	celery flower -A celery_worker.celery --loglevel=info
}

run_events(){
	echo "Start Events Monitor"
	celery events -A celery_worker.celery --loglevel=info
}

run_tests(){
	echo "Start Tests"
  gnome-terminal --working-directory=$(pwd) -x bash -c "source bin/activate; export FLASK_CONFIG=testing; celery worker -A celery_worker.celery --loglevel=info"
  python -m app.tests.test_api
}

start_app(){
	gnome-terminal --working-directory=$(pwd) -x bash -c "source bin/activate; pip install -r requirements.txt; python manage.py runserver"
	gnome-terminal --working-directory=$(pwd) -x bash -c "source bin/activate; celery worker -A celery_worker.celery --loglevel=info"
}

docker_build_all(){
	docker-compose build
}

docker_start_all(){
	docker-compose up -d
}

docker_update_services(){
	docker-compose stop
	docker-compose build
	docker-compose up -d
}

docker_logs(){
	docker-compose logs -f -t --tail=50
}

docker_stats(){
	docker stats
}

docker_stop(){
	docker-compose stop
}

docker_setup_users(){
	sh docker/mongo/create_user.sh
}

docker_setup_nodes(){
	sh docker/mongo/setup_nodes.sh
}

do_nothing(){
	echo "Invalid arguments. Please, try again."
}

docker_menu(){
  option=$1
  echo "1. Start Services"
  echo "2. Build Services"
  echo "3. Build And Start Services"
  echo "4. Logs"
  echo "5. Stats"
  echo "6. Stop"
  echo "7. Setup Mongo Users"
  echo "8. Setup Mongo Nodes"
  echo ''
  echo -n "Enter an option and press [ENTER]: $option"

  if [ -z "$1" ]
  then
	read option
  else
	printf "\n\n"
  fi

  case $option in
   	1)
      docker_start_all
      ;;
    2)
      docker_build_all
      ;;
    3)
      docker_update_services
      ;;
	4)
      docker_logs
      ;;
	5)
      docker_stats
      ;;
	6)
      docker_stop
      ;;
	7)
      docker_setup_users
      ;;
	8)
      docker_setup_nodes
      ;;
	start)
      docker_start_all
      ;;
    build)
      docker_build_all
      ;;
    up)
      docker_update_services
      ;;
	logs)
      docker_logs
      ;;
	stats)
      docker_stats
      ;;
	stop)
      docker_stop
      ;;
	users)
      docker_setup_users
      ;;
	nodes)
      docker_setup_nodes
      ;;
    *)
      do_nothing
      ;;
  esac
}

local_menu(){
  option=$1

  echo "1. Update/Install Python Requirements"
  echo "2. Start Python Dev Server"
  echo "3. Start Celery Server"
  echo "4. Start Python And Celery"
  echo "5. Start Flower Server"
  echo "6. Start Event Monitor"
  echo ''
  echo -n "Enter an option and press [ENTER]: $option"

  if [ -z "$1" ]
  then
	read option
  else
	printf "\n\n"
  fi

  case $option in
    1)
      install_requirements
      ;;
    2)
      run_server
      ;;
	3)
      run_celery
      ;;
	4)
      start_app
      ;;
	5)
      run_monitor
      ;;
	6)
      run_events
      ;;
	install)
      install_requirements
      ;;
    server)
      run_server
      ;;
	celery)
      run_celery
      ;;
	start)
      start_app
      ;;
	flower)
      run_monitor
      ;;
	events)
      run_events
      ;;
    *)
      do_nothing
      ;;
  esac
}

menu(){
  option=$1
  echo "1. Local"
  echo "2. Docker"
  echo '3. Run Tests'
  echo -n "Enter an option and press [ENTER]: $option"
  
  if [ -z "$1" ]
  then
	read option
  else
	printf "\n\n"
  fi

  case $option in
    1)
      local_menu $2
      ;;
    2)
      docker_menu $2
      ;;
	3)
      run_tests
      ;;
	tests)
		run_tests
      ;;
	local)
		local_menu $2
      ;;
	docker)
		docker_menu $2
      ;;
    *)
      do_nothing
      ;;
  esac
}

# #######################################################################################
#
# Use numbers to select a menu option or alias, like "docker" or "menu"
# Access submenu actions by passing arguments for each menu space-separated
# To enter Docker Menu and then Select the build option run: ./run.sh docker build
# Examples:
#
# ./run.sh docker build or ./run.sh 1 2 or ./run.sh docker 2 or ./run.sh 1 build
# ./run.sh local install
# ./run.sh tests
#
# #######################################################################################

menu $1 $2
