import sys

import docker

try:
    CLIENT = docker.from_env()
except docker.errors.DockerException as e:
    print("[ERROR] Can't obtain docker client!", file=sys.stderr)
    print("[ERROR] Is docker deamon running?", file=sys.stderr)
    sys.exit(-1)
