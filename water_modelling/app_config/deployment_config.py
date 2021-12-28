from __future__ import annotations

from deployment import desktop_deployer

LOCAL_DEBUG_MODE = False  # Remember to make it 'False' before uploading to DockerHub
DEPLOYER = desktop_deployer.create()
