from __future__ import annotations

import os

from deployment import docker_deployer, kubernetes_deployer, desktop_deployer

DEPLOYER = desktop_deployer.create()
DEBUG_MODE = True
