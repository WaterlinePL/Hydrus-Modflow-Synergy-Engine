from __future__ import annotations

import os
from sys import platform

from deployment import docker_deployer, kubernetes_deployer, desktop_deployer

if platform == "linux" or platform == "linux2" or platform == "darwin":
    PROJECT_ROOT = os.path.abspath("../")
else:
    PROJECT_ROOT = os.path.abspath("..\\")

LOCAL_DEBUG_MODE = False  # Remember to make it 'False' before uploading to DockerHub

CONFIG_FOLDER_NAME = "app_config"
FILE_NAME = "config.json"
CONFIG_PATH = os.path.join(PROJECT_ROOT, CONFIG_FOLDER_NAME, FILE_NAME)

ALLOWED_TYPES = ["ZIP"]
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')

DEPLOYER = desktop_deployer.create()

