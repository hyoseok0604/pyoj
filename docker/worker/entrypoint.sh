#!/bin/bash

# Mount cgroup v2
echo "+memory +cpu" > /sys/fs/cgroup/cgroup.subtree_control
chown -hR celery:celery /sys/fs/cgroup

poetry run celery -A worker.celery_app worker --loglevel INFO --concurrency 2 --uid celery --gid celery