#!/bin/bash

docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongocfg1 to start..."
  docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

docker-compose exec mongors1n1 mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongors1n1 to start..."
  docker-compose exec mongors1n1 mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

docker-compose exec mongors2n1 mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongors2n1 to start..."
  docker-compose exec mongors2n1 mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done


echo "************* CREATE CONFIG SERVER REPLICA **************"
docker-compose exec mongo mongo admin --eval "rs.initiate();sleep(1000);rs.add('mongocfg2:27019');rs.add('mongocfg3:27019');"
sleep 1
echo "*********************************************************"

echo "************* CREATE SHARD SERVER 1 REPLICA *************"
docker-compose exec mongors1n1 mongo admin --eval "rs.initiate();sleep(1000);rs.add('mongors1n2:27018');rs.add('mongors1n3:27018');"
sleep 1
echo "*********************************************************"

echo "************* CREATE SHARD SERVER 2 REPLICA *************"
docker-compose exec mongors2n1 mongo admin --eval "rs.initiate();sleep(1000);rs.add('mongors2n2:27018');rs.add('mongors2n3:27018');"
sleep 1
echo "*********************************************************"

docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
RET=$?
while [[ RET -ne 0 ]]; do
  echo "Waiting for mongo to start..."
  docker-compose exec mongo mongo admin --eval "help" > /dev/null 2>&1
  RET=$?
  sleep 1
done

echo "********************** CREATE USER **********************"
docker-compose exec mongo mongo admin --eval "db=db.getSiblingDB('wiki_history_extractor'); db.createUser({ user: 'wiki', pwd: 'wiki123', roles: [{ role: 'readWrite', db: 'wiki_history_extractor' }, { role: 'read', db: 'local' }]});"
sleep 1
echo "*********************************************************"

echo "********************* CREATE SHARDS *********************"
docker-compose exec mongo mongo admin --eval "sh.addShard('mongors1/mongors1n1:27018'); sh.addShard('mongors2/mongors2n1:27018');"
sleep 1
echo "*********************************************************"

echo "******************** ENABLE DB SHARD ********************"
docker-compose exec mongo mongo admin --eval "sh.enableSharding('wiki_history_extractor');"
sleep 1
echo "*********************************************************"

#echo "**************** ENABLE COLLECTION SHARD ****************"
#docker-compose exec mongo mongo admin --eval "db=db.getSiblingDB('wiki_history_extractor');db.revisions.ensureIndex({ _id : 'hashed'}); db.articles.ensureIndex( { _id : 'hashed' } ); sh.shardCollection('wiki_history_extractor.revisions', { '_id': 'hashed' } ); sh.shardCollection('wiki_history_extractor.articles', { '_id': 'hashed' } );"
#sleep 1
#echo "*********************************************************"

