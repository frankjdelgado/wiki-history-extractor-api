#!/bin/bash

docker-compose exec flask python -m app.tests.test_api
