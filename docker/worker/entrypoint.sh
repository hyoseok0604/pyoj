#!/bin/bash

mkdir -p /sys/fs/cgroup/init
xargs -rn1 < /sys/fs/cgroup/cgroup.procs > /sys/fs/cgroup/init/cgroup.procs || :
sed -e 's/ / +/g' -e 's/^/+/' < /sys/fs/cgroup/cgroup.controllers \
  > /sys/fs/cgroup/cgroup.subtree_control

chown -hR celery:celery /sys/fs/cgroup

poetry run celery -A worker.celery_app worker --loglevel INFO --concurrency 2 --uid celery --gid celery