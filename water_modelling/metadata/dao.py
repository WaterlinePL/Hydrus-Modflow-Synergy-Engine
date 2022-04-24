import json
import os
import shutil
from typing import List

from app_config import deployment_config
from metadata.hydrological_model_enum import HydrologicalModelEnum
from server.user_state import UserState
from metadata.project_metadata import ProjectMetadata

ProjectName = str


def create(project: ProjectMetadata):
    """
    Creates a new project in the workspace. The project consists of a root directory, which contains
    a modflow folder for the modflow model, a hydrus folder for the hydrus models, and a JSON file
    containing information about the project, as described above.

    :param project: dictionary, the representation of the project's JSON file
    :return: None
    """
    # create catalogue structure
    # TODO - check for collision?
    project_root = os.path.join(deployment_config.WORKSPACE_DIR, project['name'])
    hydrus_folder = os.path.join(project_root, 'hydrus')
    modflow_folder = os.path.join(project_root, 'modflow')
    os.mkdir(project_root)
    os.mkdir(hydrus_folder)
    os.mkdir(modflow_folder)

    # save project JSON file
    file_path = os.path.join(project_root, project['name'] + '.json')
    file = open(file_path, 'w+')
    json.dump(project, file)


def read(project_name: str) -> ProjectMetadata:
    """
    Reads and returns the JSON file for the project with the specified name.

    :param project_name: string, the name of the project whose JSON file we want to retrieve
    :return: the project's JSON file
    """
    path_to_project = os.path.join(deployment_config.WORKSPACE_DIR, project_name, project_name + ".json")
    with open(path_to_project) as handle:
        return json.load(handle, object_hook=lambda d: ProjectMetadata(**d))


def read_all() -> List[ProjectName]:
    """
    Returns a list of names of all projects existing in the system.

    :return: a list of strings, the project names
    """
    return [name for name in os.listdir(deployment_config.WORKSPACE_DIR)
            if os.path.isdir(os.path.join(deployment_config.WORKSPACE_DIR, name))]


def save_or_update(project: ProjectMetadata, state: UserState):
    """
    Updates the given fields in a given project, leaving the rest unchanged. The name field cannot be modified.
    If the project that was updated was currently loaded, the app utility will be given this updated object as well.

    TODO: DEL :param project_name: string, the project whose fields to update
    :param project: dict, the fields to be updated
    :param state: Current user's state
    :return: None
    """
    # read and update project file
    # project = read(project_name)
    # for field in project.keys():
    #     if field != "name":
    #         project[field] = project[field]

    # if that project is currently loaded, and it probably is, update the record in the utility
    # TODO: is this really needed?
    if state.loaded_project and state.loaded_project["name"] == project.name:
        state.loaded_project = project

    # write the updated project into the JSON file
    with open(os.path.join(deployment_config.WORKSPACE_DIR, project.name, project.name + ".json"), "w") as file:
        json.dump(project, file)


# TODO: this method should be in ProjectMetadataService
def remove_model(model_type: HydrologicalModelEnum, model_name: str, state: UserState):
    """
    Removes an already loaded model from the project.

    :param model_type: enum, the type of model to delete, hydrus or modflow
    :param model_name: string, the name of the hydrological model to delete
    :param state: Current user's state
    :return: None
    """

    # TODO: Use model and update it
    model_path = os.path.join(deployment_config.WORKSPACE_DIR, state.loaded_project["name"], model_type, model_name)
    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
        if model_type == HydrologicalModelEnum.MODFLOW:
            save_or_update(state.loaded_project["name"], {"modflow_model": None}, state)
        elif model_type == HydrologicalModelEnum.HYDRUS:
            new_list = state.loaded_project["hydrus_models"]
            new_list.remove(model_name)
            if new_list is None:
                new_list = []
            save_or_update(state.loaded_project["name"], {"hydrus_models": new_list}, state)


# TODO: this method should be in ProjectMetadataService
def get_hydrus_length_unit(model_name: str, state: UserState):
    """
    Extracts the length unit used for a given hydrus model.

    :param model_name: the model to get the unit fro
    :param state: Current user's state
    :return: unit, string - "m", "cm" or "mm"
    """
    filepath = os.path.join(state.get_hydrus_dir(), model_name, "SELECTOR.IN")
    selector_file = open(filepath, 'r')

    lines = selector_file.readlines()
    i = 0

    while True:
        if i >= len(lines):
            raise LookupError(f"ERROR: invalid SELECTOR.IN file for model {model_name}, no length unit found")
        curr_line = lines[i]
        if "LUnit" in curr_line:
            unit = lines[i + 1].strip()
            return unit
        i += 1


def remove_project(project_name: str, state: UserState):
    """
    Removes an existing project from the workspace

    :param project_name: the name of the project to be removed
    :param state: Current user's state
    :return: None
    """
    project_path = os.path.join(deployment_config.WORKSPACE_DIR, project_name)

    # remove project
    if os.path.isdir(project_path):
        shutil.rmtree(project_path)

    # if project was currently loaded, remove it and reset util fields
    if state.loaded_project is not None and state.loaded_project['name'] == project_name:
        state.reset_project_data()


# TODO: stuff below goes to another file
#  ----- weather file data keys -----
LATITUDE = 'Latitude'
ELEVATION = 'Elevation'
RAD = 'Solar'
T_MAX = 'Max Temperature'
T_MIN = 'Min Temperature'
RH_MEAN = 'Relative Humidity'
WIND = 'Wind'
PRECIPITATION = 'Precipitation'


def add_weather_to_hydrus_model(model_name: str, data: dict, state: UserState):
    """
    Enriches the target hydrus model with weather file data.

    :param model_name: the name of the model to modify
    :param data: a dictionary with the loaded weather data
    :param state: Current user's state
    :return: success - boolean, true if model was updated successfully, false otherwise
    """
    model_dir = os.path.join(state.get_hydrus_dir(), model_name)

    # modify meteo file if it exists, return if encountered issues
    if os.path.isfile(os.path.join(model_dir, "METEO.IN")):
        meteo_file_modified = modify_meteo_file(model_dir, data)
        if not meteo_file_modified:
            return False

    # modify atmosph file is it exists
    replace_rain = PRECIPITATION in data.keys()
    if replace_rain and os.path.isfile(os.path.join(model_dir, "ATMOSPH.IN")):
        atmosph_file_modified = modify_atmosph_file(model_dir, data)
        if not atmosph_file_modified:
            return False

    return True


def modify_meteo_file(model_dir, data):
    meteo_file_path = os.path.join(model_dir, "METEO.IN")
    meteo_file = open(meteo_file_path, "r+")

    old_file_lines = meteo_file.readlines()
    # remove trailing empty lines from end of file
    while old_file_lines[len(old_file_lines) - 1].strip() == "":
        old_file_lines.pop()
    new_file_lines = []

    # update latitude and altitude
    i = 0
    while True:
        curr_line = old_file_lines[i]
        new_file_lines.append(curr_line)
        i += 1
        if "Latitude" in curr_line:
            # write the updated values and break
            new_file_lines.append(f"   {data[LATITUDE][0]}   {data[ELEVATION][0]}\n")
            i += 1
            break

    # check which fields we have data about
    replace_rad = RAD in data.keys()
    replace_tmax = T_MAX in data.keys()
    replace_tmin = T_MIN in data.keys()
    replace_rhmean = RH_MEAN in data.keys()
    replace_wind = WIND in data.keys()

    # navigate to table start
    while True:
        curr_line = old_file_lines[i]
        new_file_lines.append(curr_line)
        i += 1
        if "Daily values" in curr_line:
            new_file_lines.append(old_file_lines[i])  # skip field descriptions line
            i += 1
            new_file_lines.append(old_file_lines[i])  # skip units line
            i += 1
            break

    # verify if weather file length is at least the same as data;
    # i+1 for 0-indexing, +1 for the sum to be correct, then -1 for the EOF line
    data_lines = len(old_file_lines) - (i + 1)
    if len(data[LATITUDE]) < data_lines:
        print(
            f"WARNING: insufficient weather file size - expected at least {data_lines} records, got {len(data[LATITUDE])}")
        return False

    # write new table values, only change columns for which we have data
    data_row = 0
    while True:

        # break if reached end of file
        curr_line = old_file_lines[i]
        if "end" in curr_line:
            new_file_lines.append(curr_line)
            break

        curr_row = old_file_lines[i].split()
        if replace_rad:
            curr_row[1] = data[RAD][data_row]
        if replace_tmax:
            curr_row[2] = data[T_MAX][data_row]
        if replace_tmin:
            curr_row[3] = data[T_MIN][data_row]
        if replace_rhmean:
            curr_row[4] = data[RH_MEAN][data_row]
        if replace_wind:
            curr_row[5] = data[WIND][data_row]

        new_file_lines.append(build_line(curr_row))

        i += 1
        data_row += 1

    # overwrite file
    meteo_file.seek(0)
    meteo_file.writelines(new_file_lines)
    meteo_file.truncate()
    meteo_file.close()

    return True


def modify_atmosph_file(model_dir, data):
    atmosph_file_path = os.path.join(model_dir, "ATMOSPH.IN")
    atmosph_file = open(atmosph_file_path, "r+")

    old_file_lines = atmosph_file.readlines()
    # remove trailing empty lines from end of file
    while old_file_lines[len(old_file_lines) - 1].strip() == "":
        old_file_lines.pop()
    new_file_lines = []

    i = 0

    # navigate to table start
    while True:
        curr_line = old_file_lines[i]
        new_file_lines.append(curr_line)
        i += 1
        if "Prec" in curr_line:
            break

    # verify if weather file length is at least the same as data;
    # i+1 for 0-indexing, +1 for the sum to be correct, then -1 for the EOF line
    data_lines = len(old_file_lines) - (i + 1)
    if len(data[LATITUDE]) < data_lines:
        print(
            f"WARNING: insufficient weather file size - expected at least {data_lines} records, got {len(data[LATITUDE])}")
        return False

    # modify table
    data_row = 0
    while True:

        # break if reached end of file
        curr_line = old_file_lines[i]
        if "end" in curr_line:
            new_file_lines.append(curr_line)
            break

        curr_row = old_file_lines[i].split()
        curr_row[1] = data[PRECIPITATION][data_row]
        new_file_lines.append(build_line(curr_row))

        i += 1
        data_row += 1

    # overwrite file
    atmosph_file.seek(0)
    atmosph_file.writelines(new_file_lines)
    atmosph_file.truncate()
    atmosph_file.close()

    return True


def build_line(items: list):
    line = "   "
    for item in items:
        line += f"{item}    "
    line += "\n"
    return line
