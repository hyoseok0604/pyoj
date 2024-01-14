#!/bin/bash

docker compose -f ./docker/compose/docker-compose.yaml -f ./docker/compose/docker-compose.prod.yaml --project-directory . $@