#!/bin/bash
docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongo to start..."
  docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

echo "********************** CREATE USER **********************"
docker-compose exec mongo mongo --eval "db=db.getSiblingDB('wiki_history_extractor'); db.createUser({ user: 'wiki', pwd: 'wiki123', roles: [{ role: 'readWrite', db: 'wiki_history_extractor' }, { role: 'read', db: 'local' }]});"
docker-compose exec mongo mongo admin --eval "db.createUser( { user: 'wiki', pwd: 'wiki123', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' } ] } )"
docker-compose exec mongo mongo admin --eval "db.grantRolesToUser( 'wiki', [{ role: 'clusterMonitor', db: 'admin'}])"
# sleep 1
echo "*********************************************************"
