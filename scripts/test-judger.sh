docker build -q -f docker/test/Dockerfile -t pyoj-test-judger:latest .
docker run --rm --cgroup-parent pyojtest.slice --privileged pyoj-test-judger:latest