#!/bin/bash

start_containers() {
    echo "Creating shared Docker network..."
    docker network create shared-network || echo "Network 'shared-network' already exists."

    echo "Cleaning MySQL volume..."
    find ./src/database/mysql-db-volume -mindepth 1 -delete

    echo "Starting containers..."
    docker-compose -f ./src/docker-compose.yaml up -d
    docker-compose -f ./src/airflow/docker-compose.yaml up -d
}

restart_containers() {
    echo "Stopping containers..."
    docker-compose -f ./src/docker-compose.yaml down
    docker-compose -f ./src/airflow/docker-compose.yaml down

    echo "Cleaning MySQL volume..."
    find ./src/database/mysql-db-volume -mindepth 1 -delete

    echo "Restarting containers..."
    docker-compose -f ./src/docker-compose.yaml up -d
    docker-compose -f ./src/airflow/docker-compose.yaml up -d
}

if [ "$1" == "start" ]; then
    start_containers
elif [ "$1" == "restart" ]; then
    restart_containers
else
    echo "Usage: $0 {start|restart}"
    exit 1
fi