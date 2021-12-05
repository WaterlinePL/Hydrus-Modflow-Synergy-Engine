from app_utils import util, get_or_none
from datapassing.shape_data import ShapeFileData
from flask import render_template, redirect, abort, jsonify, send_file
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
import local_configuration_dao as lcd


def create_project_handler(req):
    name = req.json['name']
    lat = req.json['lat']
    long = req.json["long"]
    start_date = req.json["start_date"]
    end_date = req.json["end_date"]
    spin_up = req.json["spin_up"]

    # check for name collision
    lowercase_project_names = [name.lower() for name in dao.read_all()]
    if name.lower() in lowercase_project_names:
        return jsonify(error=str("A project with this name already exists (names are case-insensitive)")), 404

    project = {
        "name": name,
        "lat": lat,
        "long": long,
        "start_date": start_date,
        "end_date": end_date,
        "spin_up": spin_up,
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
    util.reset_project_data()
    util.loaded_project = project
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


def remove_project_handler(req):
    body = json.loads(req.data)
    if body['projectName']:
        dao.remove_project(body['projectName'])
    return redirect(endpoints.PROJECT_LIST, code=303)


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

            # clear old data and load new project
            util.reset_project_data()
            util.loaded_project = chosen_project

            if util.loaded_project["modflow_model"]:
                model_path = os.path.join(util.get_modflow_dir(), util.loaded_project["modflow_model"])
                nam_file_name = modflow_utils.get_nam_file(model_path)
                model_data = modflow_utils.get_model_data(model_path, nam_file_name)
                util.recharge_masks = modflow_utils.get_shapes_from_rch(
                    model_path, nam_file_name, (model_data["rows"], model_data["cols"])
                )

            print(util.loaded_project)
            return render_template(template.PROJECT, project=chosen_project)


def project_download_handler():
    if util.loaded_project is not None:
        project_dir = os.path.join(util.workspace_dir, util.loaded_project["name"])
        zip_file = shutil.make_archive(project_dir, 'zip', project_dir)
        return send_file(zip_file, as_attachment=True)
    return '', 204


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
            prev_end=project['end_date'],
            prev_spin_up=project['spin_up']
        )


def update_project_settings(req):
    name = req.json['name']
    lat = req.json['lat']
    long = req.json["long"]
    start_date = req.json["start_date"]
    end_date = req.json["end_date"]
    spin_up = req.json['spin_up']

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
    prev_project['spin_up'] = spin_up

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
    models = req.files.getlist('archive-input')

    for model in models:
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
                return jsonify(error=str("Invalid Hydrus project structure")), 500

            # update project JSON
            updates = {
                "hydrus_models": util.loaded_project["hydrus_models"] + [model_name]
            }
            dao.update(util.loaded_project["name"], updates)

        else:
            print("Invalid archive format, must be one of: ", end='')
            print(util.allowed_types)

            return jsonify(error=str("Invalid file type. Accepted types: "+" ".join(util.allowed_types))), 500

    print("Hydrus model uploaded successfully")
    return redirect(endpoints.UPLOAD_HYDRUS)


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
    util.loaded_shapes[util.loaded_project["hydrus_models"][hydrus_model_index]] = ShapeFileData(
        shape_mask_array=np_array_shape)

    return json.dumps({'status': 'OK'})


def next_model_redirect_handler(hydrus_model_index, error_flag):
    # check if we still have models to go, if not, redirect to next section
    if hydrus_model_index >= len(util.loaded_project["hydrus_models"]):
        for key in util.loaded_shapes:
            print(key, '->\n', util.loaded_shapes[key].shape_mask)
        return redirect(endpoints.SIMULATION)

    else:
        rows_height, cols_width = modflow_utils.scale_cells_size(util.loaded_project['row_cells'],
                                                                 util.loaded_project['col_cells'], 500)
        return render_template(
            template.DEFINE_SHAPES,
            rowAmount=util.loaded_project["rows"],
            colAmount=util.loaded_project["cols"],
            rows=[str(x) for x in range(util.loaded_project["rows"])],
            cols=[str(x) for x in range(util.loaded_project["cols"])],
            cols_width=cols_width,
            rows_height=rows_height,
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
        rows_height, cols_width = modflow_utils.scale_cells_size(util.loaded_project['row_cells'],
                                                                 util.loaded_project['col_cells'], 500)
        return render_template(template.RCH_SHAPES, hydrus_models=util.loaded_project["hydrus_models"],
                               shape_mask=util.recharge_masks[rch_shape_index], rch_shape_index=rch_shape_index,
                               rows_height=rows_height, cols_width=cols_width, current_model=current_model)


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

    lcd.update_configuration(hydrus_exe, modflow_exe)

    return json.dumps({'status': 'OK'})


def simulation_summary_handler():
    rows_height, cols_width = modflow_utils.scale_cells_size(util.loaded_project['row_cells'],
                                                             util.loaded_project['col_cells'], 500)

    return render_template(
        template.SIMULATION,
        modflow_proj=util.loaded_project["modflow_model"],
        shapes=util.loaded_shapes,
        cols_width=cols_width,
        rows_height=rows_height,
    )
