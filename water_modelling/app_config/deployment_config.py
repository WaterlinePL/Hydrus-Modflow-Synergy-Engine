from __future__ import annotations

from deployment import docker_deployer

LOCAL_DEBUG_MODE = False  # Remember to make it 'False' before uploading to DockerHub
DEPLOYER = docker_deployer.create()
