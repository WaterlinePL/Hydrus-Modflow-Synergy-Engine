import json
import os
import shutil

from app_utils import AppUtils

"""
A project .json file contains the following:
{
    "name": string - the name of the project, must match root catalogue,
    "lat": float - the latitude the model lies at,
    "long": float - the longitude the model lies at,
    "start_date": string - the start date of the simulation, YYYY-mm-dd
    "end_date": string - the end date of the simulation, YYYY-mm-dd,
    "rows": int - the amount of rows in the model grid,
    "cols": int - the amount of columns in the model grid,
    "grid_unit": string - the unit in which the model grid size is represented; "feet", "meters", "centimeters" or null,
    "row_cells": List<Float> - the heights of the model's consecutive rows,
    "col_cells": List<Float> - the widths of the model's consecutive columns,
    "modflow_model": string - the name of the folder containing the modflow model,
    "hydrus_models": List<String> - a list of names of folders containing the hydrus models
}
"""

WORKSPACE_PATH = "../../workspace"


def create(project: dict):
    """
    Creates a new project in the workspace. The project consists of a root directory, which contains
    a modflow folder for the modflow model, a hydrus folder for the hydrus models, and a JSON file
    containing information about the project, as described above.

    :param project: dictionary, the representation of the project's JSON file
    :return: None
    """
    # create catalogue structure
    # TODO - check for collision?
    project_root = os.path.join(WORKSPACE_PATH, project['name'])
    hydrus_folder = os.path.join(project_root, 'hydrus')
    modflow_folder = os.path.join(project_root, 'modflow')
    os.mkdir(project_root)
    os.mkdir(hydrus_folder)
    os.mkdir(modflow_folder)

    # save project JSON file
    file_path = os.path.join(project_root, project['name']+'.json')
    file = open(file_path, 'w+')
    json.dump(project, file)


def read(project_name: str):
    """
    Reads and returns the JSON file for the project with the specified name.

    :param project_name: string, the name of the project whose JSON file we want to retrieve
    :return: the project's JSON file
    """
    return json.load(open(os.path.join(WORKSPACE_PATH, project_name, project_name+".json")))


def read_all():
    """
    Returns a list of names of all projects existing in the system.

    :return: a list of strings, the project names
    """
    return [name for name in os.listdir(WORKSPACE_PATH) if os.path.isdir(os.path.join(WORKSPACE_PATH, name))]


def update(project_name: str, changed_fields: dict, util: AppUtils):
    """
    Updates the given fields in a given project, leaving the rest unchanged. The name field cannot be modified.
    If the project that was updated was currently loaded, the app utility will be given this updated object as well.

    :param project_name: string, the project whose fields to update
    :param changed_fields: dict, the fields to be updated
    :param util: the app utility; this has to be passed as a parameter to avoid circular imports
    :return: None
    """
    # read and update project file
    project = read(project_name)
    for field in changed_fields.keys():
        if field != "name":
            project[field] = changed_fields[field]

    # if that project is currently loaded, and it probably is, update the record in the utility
    if util.loaded_project["name"] == project_name:
        util.loaded_project = project

    # write the updated project into the JSON file
    file = open(os.path.join(WORKSPACE_PATH, project_name, project_name+".json"), "w")
    json.dump(project, file)


def remove_model(model_type: str, model_name: str, util: AppUtils):
    """
    Removes an already loaded model from the project.

    :param model_type: string, the type of model to delete, "hydrus" or "modflow"
    :param model_name: string, the name of the model to delete
    :param util: the app utility
    :return: None
    """
    model_path = os.path.join(WORKSPACE_PATH, util.loaded_project["name"], model_type, model_name)
    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
        if model_type == 'modflow':
            update(util.loaded_project["name"], {"modflow_model": None}, util)
        else:
            new_list = util.loaded_project["hydrus_models"]
            new_list.remove(model_name)
            print(new_list)
            if new_list is None:
                new_list = []
            update(util.loaded_project["name"], {"hydrus_models": new_list}, util)
