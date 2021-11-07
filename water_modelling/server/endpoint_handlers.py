from app_utils import AppUtils, get_or_none
import numpy as np
from flask import render_template, redirect, abort
from zipfile import ZipFile
from datapassing.shape_data import ShapeFileData
import DAO
import shutil

import os
import json

from modflow import modflow_utils
from server import endpoints, template

util = AppUtils()
util.setup()


def create_project_handler(req):
    name = req.form['name']
    lat = get_or_none(req, "lat")
    long = get_or_none(req, "long")
    start_date = get_or_none(req, "start_date")
    end_date = get_or_none(req, "end_date")
    project = {
        "name": name,
        "lat": lat,
        "long": long,
        "start_date": start_date,
        "end_date": end_date,
        # everything below here will be populated once modflow and hydrus models are loaded
        "rows": None,
        "cols": None,
        "grid_unit": None,
        "row_cells": [],
        "col_cells": [],
        "modflow_model": None,
        "hydrus_models": []
    }
    DAO.create(project)
    util.loaded_project = project
    return redirect(endpoints.PROJECT_NO_ID)


def project_list_handler():
    return render_template(template.PROJECT_LIST, projects=DAO.read_all())


def project_handler(project_name):
    if project_name is None:
        # case 1 - there is already a project loaded and we just want to see it
        if util.loaded_project is not None:
            return render_template(template.PROJECT, project=util.loaded_project)
        # case 2 - there is no project loaded, the user should be redirected to the project list to select a project
        else:
            return redirect(endpoints.PROJECT_LIST)
    # case 3 - there is no project selected, but we're just selecting one
    else:
        chosen_project = DAO.read(project_name)
        # case 3a - the project does not exist
        if chosen_project is None:
            return redirect(endpoints.PROJECT_LIST)
        else:
            util.loaded_project = chosen_project
            print(util.loaded_project)
            return render_template(template.PROJECT, project=chosen_project)


def upload_modflow_handler(req):

    # every uploaded model needs to belong to a project;
    # if there is no active project, we cannot upload a model
    if util.loaded_project is None:
        return redirect(endpoints.PROJECT_LIST)

    model = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(model.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.get_modflow_dir(), model.filename)
        model.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the model name and remember it
            model_name = model.filename.split('.')[0]

            # create a dedicated catalogue and load the model into it
            model_path = os.path.join(util.get_modflow_dir(), model_name)
            os.system('mkdir ' + model_path)
            archive.extractall(model_path)

            # validate model
            util.nam_file_name = modflow_utils.get_nam_file(model_path)
            invalid_model = not modflow_utils.validate_model(model_path, util.nam_file_name)

        os.remove(archive_path)
        if invalid_model:
            shutil.rmtree(model_path, ignore_errors=True)  # remove invalid model dir
            return abort(500)

        # if model is valid, read its parameters and store them
        model_data = modflow_utils.get_model_data(model_path, util.nam_file_name)

        util.modflow_rows, util.modflow_cols = model_data["rows"], model_data["cols"]
        util.recharge_masks = modflow_utils.get_shapes_from_rch(model_path, util.nam_file_name,
                                                                (util.modflow_rows, util.modflow_cols))

        # update project JSON
        updates = {
            "modflow_model": model_name,
            "rows": model_data["rows"],
            "cols": model_data["cols"],
            "grid_unit": model_data["grid_unit"],
            "row_cells": model_data["row_cells"],
            "col_cells": model_data["col_cells"]
        }
        DAO.update(util.loaded_project["name"], updates, util)

        print("Modflow model uploaded successfully")
        return redirect(endpoints.UPLOAD_MODFLOW)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return abort(500)


def upload_hydrus_handler(req):
    model = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(model.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.get_hydrus_dir(), model.filename)
        model.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the model name and remember it
            model_name = model.filename.split('.')[0]

            # create a dedicated catalogue and load the model into it
            os.system('mkdir ' + os.path.join(util.get_hydrus_dir(), model_name))
            archive.extractall(os.path.join(util.get_hydrus_dir(), model_name))

        os.remove(archive_path)

        # update project JSON
        updates = {
            "hydrus_models": util.loaded_project["hydrus_models"] + [model_name]
        }
        DAO.update(util.loaded_project["name"], updates, util)

        print("Hydrus model uploaded successfully")
        return redirect(endpoints.UPLOAD_HYDRUS)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_shape_handler(req, hydrus_model_index):
    # if not yet done, initialize the shape arrays list to the amount of models
    if len(util.loaded_shapes) < len(util.loaded_project["hydrus_models"]):

        for hydrus_model in util.loaded_project["hydrus_models"]:
            util.loaded_shapes[hydrus_model] = None
        # util.loaded_shapes = [None for _ in range(len(util.loaded_project["hydrus_models"]))]

    # read the array from the request and store it
    shape_array = req.get_json(force=True)
    np_array_shape = np.array(shape_array)
    util.loaded_shapes[util.loaded_project["hydrus_models"][hydrus_model_index]] = ShapeFileData(shape_mask_array=np_array_shape)

    return json.dumps({'status': 'OK'})


def next_model_redirect_handler(hydrus_model_index, error_flag):
    # check if we still have models to go, if not, redirect to next section
    if hydrus_model_index >= len(util.loaded_project["hydrus_models"]):
        for key in util.loaded_shapes:
            print(key, '->\n', util.loaded_shapes[key].shape_mask)
        return redirect(endpoints.SIMULATION)

    else:
        return render_template(
            template.DEFINE_SHAPES,
            rowAmount=util.modflow_rows,
            colAmount=util.modflow_cols,
            rows=[str(x) for x in range(util.modflow_rows)],
            cols=[str(x) for x in range(util.modflow_cols)],
            modelIndex=hydrus_model_index,
            modelName=util.loaded_project["hydrus_models"][hydrus_model_index],
            upload_error=error_flag
        )
