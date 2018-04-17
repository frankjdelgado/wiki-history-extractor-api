#!/bin/bash
exec docker-compose down && docker system prune -f --volumes
