import json
import os

"""
A project .json file contains the following:
{
    "name": string - the name of the project, must match root catalogue,
    "rows": int - the amount of rows in the model grid,
    "cols": int - the amount of columns in the model grid,
    "cell_size": float - the length of a single grid cell,
    "lat": float - the latitude the model lies at,
    "long": float - the longitude the model lies at,
    "start_date": string - the start date of the simulation, YYYY-mm-dd
    "end_date": string - the end date of the simulation, YYYY-mm-dd,
    "modflow_model": string - the name of the folder containing the modflow model,
    "hydrus_models": List<String> - a list of names of folders containing the hydrus models
}
"""

WORKSPACE_PATH = "../../workspace"


def create(document: dict):
    pass


def read(project_name: str):
    return json.load(open(os.path.join(WORKSPACE_PATH, project_name, project_name+".json")))


def read_all():
    """
    Returns a list of names of all projects existing in the system.

    :return: a list of strings, project names
    """
    return [name for name in os.listdir(WORKSPACE_PATH) if os.path.isdir(os.path.join(WORKSPACE_PATH, name))]

