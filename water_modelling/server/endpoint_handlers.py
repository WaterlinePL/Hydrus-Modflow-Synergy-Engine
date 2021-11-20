from app_utils import util, get_or_none
from datapassing.shape_data import ShapeFileData
from flask import render_template, redirect, abort, jsonify
from flask_paginate import Pagination, get_page_args
from hydrus import hydrus_utils
from modflow import modflow_utils
from server import endpoints, template
from zipfile import ZipFile

import dao
import json
import numpy as np
import os
import shutil


def create_project_handler(req):
    name = req.json['name']
    lat = req.json['lat']
    long = req.json["long"]
    start_date = req.json["start_date"]
    end_date = req.json["end_date"]

    # check for name collision
    if name in dao.read_all():
        return jsonify(error=str("A project with this name already exists")), 404

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
    dao.create(project)
    util.loaded_project = project
    #TODO: czy powinnismy tutaj czy�ci� utils???
    return json.dumps({'status': 'OK'})


def get_projects(projects, offset=0, per_page=10):
    return projects[offset: offset + per_page]


def project_list_handler(search):
    projects = dao.read_all()

    if search:
        projects = [p for p in projects if search.lower() in p.lower()]

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination_projects = get_projects(projects=projects, offset=offset, per_page=per_page)
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=len(projects),
                            record_name="projects",
                            css_framework='bootstrap4')

    return render_template(template.PROJECT_LIST,
                           search_value=search,
                           projects=pagination_projects,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           error_project_name=util.get_error_flag()
                           )


def project_handler(project_name):
    if project_name is None:
        # case 1 - there is already a project loaded and we just want to see it
        if util.loaded_project is not None:
            return render_template(template.PROJECT, project=util.loaded_project)
        # case 2 - there is no project loaded, the user should be redirected to the project list to select a project
        else:
            util.error_flag = True
            return redirect(endpoints.PROJECT_LIST)
    # case 3 - we're selecting a new project
    else:
        try:
            chosen_project = dao.read(project_name)
        # case 3a - the project does not exist
        except FileNotFoundError:
            util.error_flag = True
            return redirect(endpoints.PROJECT_LIST)
        else:
            util.loaded_project = chosen_project

            # make sure to clear out any data entered for a previous project
            util.current_method = None
            util.models_masks_ids = {}
            util.recharge_masks = []
            util.loaded_shapes = {}

            print(util.loaded_project)
            return render_template(template.PROJECT, project=chosen_project)


def edit_project_handler(project_name):
    try:
        project = dao.read(project_name)
    except FileNotFoundError:
        util.error_flag = True
        return redirect(endpoints.PROJECT_LIST)
    else:
        return render_template(
            template.CREATE_PROJECT,
            name=project_name,
            prev_lat=project['lat'],
            prev_long=project['long'],
            prev_start=project['start_date'],
            prev_end=project['end_date']
        )


def update_project_settings(req):
    name = req.json['name']
    lat = req.json['lat']
    long = req.json["long"]
    start_date = req.json["start_date"]
    end_date = req.json["end_date"]

    try:
        prev_project = dao.read(name)
    except FileNotFoundError:
        util.error_flag = True
        return redirect(endpoints.PROJECT_LIST)

    prev_project["name"] = name
    prev_project["lat"] = lat
    prev_project["long"] = long
    prev_project["start_date"] = start_date
    prev_project["end_date"] = end_date

    dao.update(name, prev_project)
    return json.dumps({'status': 'OK'})


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
            nam_file_name = modflow_utils.get_nam_file(model_path)
            invalid_model = not modflow_utils.validate_model(model_path, nam_file_name)

        os.remove(archive_path)
        if invalid_model:
            shutil.rmtree(model_path, ignore_errors=True)  # remove invalid model dir
            return abort(500)

        # if model is valid, read its parameters and store them
        model_data = modflow_utils.get_model_data(model_path, nam_file_name)

        util.recharge_masks = modflow_utils.get_shapes_from_rch(model_path, nam_file_name,
                                                                (model_data["rows"], model_data["cols"]))

        # update project JSON
        updates = {
            "modflow_model": model_name,
            "rows": model_data["rows"],
            "cols": model_data["cols"],
            "grid_unit": model_data["grid_unit"],
            "row_cells": model_data["row_cells"],
            "col_cells": model_data["col_cells"]
        }
        dao.update(util.loaded_project["name"], updates)

        print("Modflow model uploaded successfully")
        return redirect(endpoints.UPLOAD_MODFLOW)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return abort(500)


def remove_modflow_handler(req):
    body = json.loads(req.data)
    if body['modelName']:
        dao.remove_model('modflow', body["modelName"])
    return redirect(endpoints.UPLOAD_MODFLOW, code=303)


def upload_hydrus_handler(req):
    model = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(model.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.get_hydrus_dir(), model.filename)
        model.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            model_name = model.filename.split('.')[0]
            project_path = os.path.join(util.get_hydrus_dir(), model_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + project_path)
            archive.extractall(project_path)

            # validate model
            invalid_model = not hydrus_utils.validate_model(project_path)

        os.remove(archive_path)
        if invalid_model:
            shutil.rmtree(project_path, ignore_errors=True)  # remove invalid project dir
            return abort(500)

        # update project JSON
        updates = {
            "hydrus_models": util.loaded_project["hydrus_models"] + [model_name]
        }
        dao.update(util.loaded_project["name"], updates)

        print("Hydrus model uploaded successfully")
        return redirect(endpoints.UPLOAD_HYDRUS)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def remove_hydrus_handler(req):
    body = json.loads(req.data)
    print("received call")
    print(body['modelName'])
    if body['modelName']:
        dao.remove_model('hydrus', body["modelName"])
    return redirect(endpoints.UPLOAD_HYDRUS, code=303)


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
            rowAmount=util.loaded_project["rows"],
            colAmount=util.loaded_project["cols"],
            rows=[str(x) for x in range(util.loaded_project["rows"])],
            cols=[str(x) for x in range(util.loaded_project["cols"])],
            modelIndex=hydrus_model_index,
            modelName=util.loaded_project["hydrus_models"][hydrus_model_index],
            upload_error=error_flag
        )


def next_shape_redirect_handler(rch_shape_index):
    if rch_shape_index >= len(util.recharge_masks):
        util.get_shapes_from_masks_ids()
        for key in util.loaded_shapes:
            print(key, '->\n', util.loaded_shapes[key].shape_mask)
        return redirect(endpoints.SIMULATION)
    else:
        current_model = util.get_current_model_by_id(rch_shape_index)

        return render_template(template.RCH_SHAPES, hydrus_models=util.loaded_project["hydrus_models"],
                               shape_mask=util.recharge_masks[rch_shape_index], rch_shape_index=rch_shape_index,
                               current_model=current_model)


def assign_model_to_shape(req, rch_shape_index):
    hydrus_model_name = req.json["hydrusModel"]
    previos_hydrus_model_name = req.json["previousModel"]

    if previos_hydrus_model_name:
        util.models_masks_ids[previos_hydrus_model_name].remove(rch_shape_index)

    if hydrus_model_name == "":
        return json.dumps({'status': 'OK'})

    if util.models_masks_ids[hydrus_model_name] is None:
        util.models_masks_ids[hydrus_model_name] = [rch_shape_index]
    else:
        util.models_masks_ids[hydrus_model_name].append(rch_shape_index)

    return json.dumps({'status': 'OK'})


def upload_new_configurations(req):
    modflow_exe = req.json['modflowExe']
    hydrus_exe = req.json['hydrusExe']
    print(modflow_exe, hydrus_exe)

    if not os.path.exists(modflow_exe):
        return jsonify(error=str("Incorrect Modflow exe path"), model=str("modflow")), 404

    if not os.path.exists(hydrus_exe):
        return jsonify(error=str("Incorrect Hydrus exe path"), model=str("hydrus")), 404

    util.modflow_exe = modflow_exe
    util.hydrus_exe = hydrus_exe

    return json.dumps({'status': 'OK'})
