#!/bin/bash

docker exec -it mongocfg1 mongo admin --port 27019 --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongocfg1 to start..."
  docker exec -it mongocfg1 mongo admin --port 27019 --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

docker exec -it mongors1n1 mongo admin --port 27018 --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongors1n1 to start..."
  docker exec -it mongors1n1 mongo admin --port 27018 --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

docker exec -it mongors2n1 mongo admin --port 27018 --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongors2n1 to start..."
  docker exec -it mongors2n1 mongo admin --port 27018 --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done


echo "************* CREATE CONFIG SERVER REPLICA **************"
docker exec -it mongocfg1 mongo admin --port 27019 --eval "rs.initiate({_id: 'configrs',configsvr: true, members: [{_id: 0, host: 'mongocfg1:27019' }, {_id: 1, host: 'mongocfg2:27019' }, {_id: 2, host: 'mongocfg3:27019'} ]});sleep(1000)"
sleep 1
echo "*********************************************************"

echo "************* CREATE SHARD SERVER 1 REPLICA *************"
docker exec -it mongors1n1 mongo admin --port 27018 --eval "rs.initiate({_id: 'mongors1', members: [{_id: 0, host: 'mongors1n1:27018' }, {_id: 1, host: 'mongors1n2:27018' }, {_id: 2, host: 'mongors1n3:27018'} ]});sleep(1000);"
sleep 1
echo "*********************************************************"

echo "************* CREATE SHARD SERVER 2 REPLICA *************"
docker exec -it mongors2n1 mongo admin --port 27018 --eval "rs.initiate({_id: 'mongors2', members: [{_id: 0, host: 'mongors2n1:27018' }, {_id: 1, host: 'mongors2n2:27018' }, {_id: 2, host: 'mongors2n3:27018'} ]});sleep(1000);"
sleep 1
echo "*********************************************************"

docker exec -it mongo mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongo to start..."
  docker exec -it mongo mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

echo "********************* CREATE SHARDS *********************"
docker exec -it mongo mongo admin --eval "sh.addShard('mongors1/mongors1n1:27018'); sh.addShard('mongors2/mongors2n1:27018');"
sleep 1
echo "*********************************************************"

echo "********************* CREATE COLLECTIONS *********************"
docker exec -it mongors1n1 bash -c "echo 'use wiki_history_extractor' | mongo admin --port 27018"
docker exec -it mongors2n1 bash -c "echo 'use wiki_history_extractor' | mongo admin --port 27018"
docker exec -it mongors1n1 bash -c "echo 'db.createCollection(\"wiki_history_extractor.article\")' | mongo admin --port 27018"
docker exec -it mongors1n1 bash -c "echo 'db.createCollection(\"wiki_history_extractor.revisions\")' | mongo admin --port 27018"
docker exec -it mongors2n1 bash -c "echo 'db.createCollection(\"wiki_history_extractor.revisions\")' | mongo admin --port 27018"
docker exec -it mongors2n1 bash -c "echo 'db.createCollection(\"wiki_history_extractor.article\")' | mongo admin --port 27018"
echo "********************* CREATE COLLECTIONS *********************"

echo "********************** CREATE USER **********************"
docker exec -it mongo mongo admin --eval "db=db.getSiblingDB('wiki_history_extractor'); db.createUser({ user: 'wiki', pwd: 'wiki123', roles: [{ role: 'readWrite', db: 'wiki_history_extractor' }, { role: 'read', db: 'local' }]});"
sleep 1
echo "*********************************************************"


echo "******************** ENABLE DB SHARD ********************"
docker exec -it mongo mongo admin --eval "sh.enableSharding('wiki_history_extractor');"
sleep 1
echo "*********************************************************"

#echo "**************** ENABLE COLLECTION SHARD ****************"
#docker exec -it mongo mongo admin --eval "db=db.getSiblingDB('wiki_history_extractor');db.revisions.ensureIndex({ _id : 'hashed'}); db.articles.ensureIndex( { _id : 'hashed' } ); sh.shardCollection('wiki_history_extractor.revisions', { '_id': 'hashed' } ); sh.shardCollection('wiki_history_extractor.articles', { '_id': 'hashed' } );"
#sleep 1
#echo "*********************************************************"
