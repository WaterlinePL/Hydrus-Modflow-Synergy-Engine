from user_state import util

import json
import os

"""
Config .json file specification:
{
    "hydrus_exe": string - current path to hydrus program executable file
    "modflow_exe": string - current path to modflow program executable file
}
"""
CONFIG_FOLDER_NAME = "app_config"
FILE_NAME = "config.json"
CONFIG_PATH = os.path.join(util.project_root, CONFIG_FOLDER_NAME, FILE_NAME)


def read_configuration():
    if not os.path.exists(CONFIG_PATH):
        update_configuration(None, None)

    return json.load(open(CONFIG_PATH))


def update_configuration(hydrus_exe, modflow_exe):
    config = {
        "hydrus_exe": hydrus_exe,
        "modflow_exe": modflow_exe
    }

    file_desc = open(CONFIG_PATH, "w")
    json.dump(config, file_desc)

