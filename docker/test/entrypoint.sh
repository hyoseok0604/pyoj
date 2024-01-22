#!/bin/bash

# Mount cgroup v2
echo "+memory +cpu" > /sys/fs/cgroup/cgroup.subtree_control
chown -hR test:test /sys/fs/cgroup

chown test:test /src

su test --command "poetry run pytest"