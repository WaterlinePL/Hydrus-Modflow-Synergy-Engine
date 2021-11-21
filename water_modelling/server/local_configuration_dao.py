from app_utils import util

import json
import os

"""
Config .json file specification:
{
    "hydrus_exe": string - current path to hydrus program executable file
    "modflow_exe": string - current path to modflow program executable file
}
"""

CONFIG_PATH = util.project_root+"app_config"
FILE_NAME = "config.json"


def read_configuration():
    if not os.path.exists(CONFIG_PATH):
        update_configuration(None, None)

    return json.load(open(os.path.join(CONFIG_PATH, FILE_NAME)))


def update_configuration(hydrus_exe, modflow_exe):
    if not os.path.exists(CONFIG_PATH):
        os.mkdir(CONFIG_PATH)

    config = {
        "hydrus_exe": hydrus_exe,
        "modflow_exe": modflow_exe
    }

    file_desc = open(os.path.join(CONFIG_PATH, FILE_NAME), "w")
    json.dump(config, file_desc)

