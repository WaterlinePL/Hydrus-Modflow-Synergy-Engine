from __future__ import annotations

import os
from sys import platform
from deployment import kubernetes_deployer

if platform == "linux" or platform == "linux2" or platform == "darwin":
    PROJECT_ROOT = os.path.abspath("../")
else:
    PROJECT_ROOT = os.path.abspath("..\\")

# Logs more info on console (ex. logs from hydrological simulation)
LOCAL_DEBUG_MODE = False  # Remember to make it 'False' before uploading to DockerHub

CONFIG_FOLDER_NAME = "app_config"
CONFIG_FILE_NAME = "config.json"

CONFIG_FOLDER_PATH = os.path.join(PROJECT_ROOT, CONFIG_FOLDER_NAME)
CONFIG_FILE_PATH = os.path.join(CONFIG_FOLDER_PATH, CONFIG_FILE_NAME)

ALLOWED_TYPES = ["ZIP"]
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, 'workspace')
DEPLOYER = kubernetes_deployer.create()
