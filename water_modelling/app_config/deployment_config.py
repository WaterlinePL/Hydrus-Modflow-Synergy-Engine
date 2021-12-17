from __future__ import annotations

import os

from deployment import docker_deployer, kubernetes_deployer, desktop_deployer

LOCAL_DEBUG_MODE = False  # Remember to make it 'False' before uploading to DockerHub
DEPLOYER = desktop_deployer.create()
