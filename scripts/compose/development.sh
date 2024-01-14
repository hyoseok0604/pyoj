#!/bin/bash

docker compose -f ./docker/compose/docker-compose.yaml -f ./docker/compose/docker-compose.dev.yaml --project-directory . --env-file ./.env $@