import json
import os
import shutil

from app_utils import util

"""
A project .json file contains the following:
{
    "name": string - the name of the project, must match root catalogue,
    "lat": float - the latitude the model lies at,
    "long": float - the longitude the model lies at,
    "start_date": string - the start date of the simulation, YYYY-mm-dd
    "end_date": string - the end date of the simulation, YYYY-mm-dd,
    "spin_up": float - how many days of hydrus simulation should be ignored,
    "rows": int - the amount of rows in the model grid,
    "cols": int - the amount of columns in the model grid,
    "grid_unit": string - the unit in which the model grid size is represented; "feet", "meters", "centimeters" or null,
    "row_cells": List<Float> - the heights of the model's consecutive rows,
    "col_cells": List<Float> - the widths of the model's consecutive columns,
    "modflow_model": string - the name of the folder containing the modflow model,
    "hydrus_models": List<String> - a list of names of folders containing the hydrus models
}
"""


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
    project_root = os.path.join(util.workspace_dir, project['name'])
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
    return json.load(open(os.path.join(util.workspace_dir, project_name, project_name+".json")))


def read_all():
    """
    Returns a list of names of all projects existing in the system.

    :return: a list of strings, the project names
    """
    return [name for name in os.listdir(util.workspace_dir) if os.path.isdir(os.path.join(util.workspace_dir, name))]


def update(project_name: str, changed_fields: dict):
    """
    Updates the given fields in a given project, leaving the rest unchanged. The name field cannot be modified.
    If the project that was updated was currently loaded, the app utility will be given this updated object as well.

    :param project_name: string, the project whose fields to update
    :param changed_fields: dict, the fields to be updated
    :return: None
    """
    # read and update project file
    project = read(project_name)
    for field in changed_fields.keys():
        if field != "name":
            project[field] = changed_fields[field]

    # if that project is currently loaded, and it probably is, update the record in the utility
    if util.loaded_project and util.loaded_project["name"] == project_name:
        util.loaded_project = project

    # write the updated project into the JSON file
    file = open(os.path.join(util.workspace_dir, project_name, project_name+".json"), "w")
    json.dump(project, file)


def remove_model(model_type: str, model_name: str):
    """
    Removes an already loaded model from the project.

    :param model_type: string, the type of model to delete, "hydrus" or "modflow"
    :param model_name: string, the name of the model to delete
    :return: None
    """
    model_path = os.path.join(util.workspace_dir, util.loaded_project["name"], model_type, model_name)
    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
        if model_type == 'modflow':
            update(util.loaded_project["name"], {"modflow_model": None})
        else:
            new_list = util.loaded_project["hydrus_models"]
            new_list.remove(model_name)
            print(new_list)
            if new_list is None:
                new_list = []
            update(util.loaded_project["name"], {"hydrus_models": new_list})


def remove_project(project_name: str):
    """
    Removes an existing project from the workspace

    :param project_name: the name of the project to be removed
    :return: None
    """
    project_path = os.path.join(util.workspace_dir, project_name)

    # remove project
    if os.path.isdir(project_path):
        shutil.rmtree(project_path)

    # if project was currently loaded, remove it and reset util fields
    if util.loaded_project is not None and util.loaded_project['name'] == project_name:
        util.reset_project_data()


def get_hydrus_length_unit(model_name: str):
    """
    Extracts the length unit used for a given hydrus model.

    :param model_name: the model to get the unit fro
    :return: unit, string - "m", "cm" or "mm"
    """
    filepath = os.path.join(util.get_hydrus_dir(), model_name, "SELECTOR.IN")
    selector_file = open(filepath, 'r')

    lines = selector_file.readlines()
    i = 0

    while True:
        if i >= len(lines):
            raise LookupError(f"ERROR: invalid SELECTOR.IN file for model {model_name}, no length unit found")
        curr_line = lines[i]
        if "LUnit" in curr_line:
            unit = lines[i+1].strip()
            return unit
        i += 1


#  ----- SWAT data keys -----
DATE = 'Date'
LATITUDE = 'Latitude'
ELEVATION = 'Elevation'
RAD = 'Solar'
T_MAX = 'Max Temperature'
T_MIN = 'Min Temperature'
RH_MEAN = 'Relative Humidity'
WIND = 'Wind'
PRECIPITATION = 'Precipitation'


def update_hydrus_model(model_name: str, data: dict):
    """
    Enriches the target hydrus model with weather file data.

    :param model_name: the name of the model to modify
    :param data: a dictionary with the loaded weather data
    :return: success - boolean, true if model was updated successfully, false otherwise
    """
    model_dir = os.path.join(util.get_hydrus_dir(), model_name)

    # modify meteo file if it exists, return if encountered issues
    if os.path.isfile(os.path.join(model_dir, "METEO.IN")):
        meteo_file_modified = modify_meteo_file(model_dir, data)
        if not meteo_file_modified:
            return False

    # modify atmosph file is it exists
    replace_rain = PRECIPITATION in data.keys()
    if replace_rain and os.path.isfile(os.path.join(model_dir, "ATMOSPH.IN")):
        modify_atmosph_file(model_dir, data)

    return True


def modify_meteo_file(model_dir, data):
    meteo_file_path = os.path.join(model_dir, "METEO.IN")
    meteo_file = open(meteo_file_path, "r+")

    old_file_lines = meteo_file.readlines()
    # remove trailing empty lines from end of file
    while old_file_lines[len(old_file_lines)-1].strip() == "":
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
    data_lines = len(old_file_lines) - (i+1)
    if len(data[data.keys()[0]]) < data_lines:
        print(f"WARNING: insufficient weather file size - expected at least {data_lines} records, got {len(data['Date'])}")
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
    while old_file_lines[len(old_file_lines)-1].strip() == "":
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
