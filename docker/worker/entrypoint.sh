#!/bin/bash

# https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt

# Mount root cgroups
if [ ! -d "/cgroups" ]; then
  mkdir /cgroups
fi

mount -t tmpfs cgroup_root /cgroups

# Create directory and setting for cgroup memory
if [ ! -d "/cgroups/memory" ]; then
  mkdir /cgroups/memory
fi

mount -t cgroup -o memory memory /cgroups/memory
chown -hR celery:celery /cgroups/memory
chmod -R +w /cgroups/memory

# Create directory and setting for cgroup cpuacct
if [ ! -d "/cgroups/cpuacct" ]; then
  mkdir /cgroups/cpuacct
fi

mount -t cgroup -o cpuacct cpuacct /cgroups/cpuacct
chown -hR celery:celery /cgroups/cpuacct
chmod -R +w /cgroups/cpuacct

poetry run celery -A worker.celery_app worker --loglevel INFO --concurrency 2 --uid celery --gid celery