from __future__ import annotations

import deployment.desktop_deployer as desktop_deployer
from deployment import docker_deployer

DEPLOYER = desktop_deployer.create()
DEBUG_MODE = True
