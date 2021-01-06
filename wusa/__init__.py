# -*- coding: utf-8 -*-
import sys

import docker

try:
    CLIENT = docker.from_env()
except docker.errors.DockerException:
    print("[ERROR] Can't obtain docker client!", file=sys.stderr)
    print("[ERROR] Is docker deamon running?", file=sys.stderr)
    sys.exit(-1)
