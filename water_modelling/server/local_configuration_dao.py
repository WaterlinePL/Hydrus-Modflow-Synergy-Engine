import json
import os

from app_config import deployment_config

"""
Config .json file specification:
{
    "hydrus_exe": string - current path to hydrus program executable file
    "modflow_exe": string - current path to modflow program executable file
}
"""


def read_configuration():
    if not os.path.exists(deployment_config.CONFIG_FILE_PATH):
        os.makedirs(deployment_config.CONFIG_FOLDER_PATH, exist_ok=True)
        update_configuration(None, None)

    return json.load(open(deployment_config.CONFIG_FILE_PATH))


def update_configuration(hydrus_exe, modflow_exe):
    config = {
        "hydrus_exe": hydrus_exe,
        "modflow_exe": modflow_exe
    }

    file_desc = open(deployment_config.CONFIG_FILE_PATH, "w")
    json.dump(config, file_desc)
