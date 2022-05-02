from typing import Tuple
from app_config import deployment_config
from datapassing.shape_data import ShapeMetadata
from flask import render_template, redirect, abort, jsonify, send_file, request
from flask_paginate import Pagination, get_page_args

from deployment import daos
from hydrus import hydrus_utils
from metadata.hydrological_model_enum import HydrologicalModelEnum
from metadata.project_metadata import ProjectMetadata
from modflow import modflow_utils
from server import endpoints, template
from zipfile import ZipFile
from utils import path_formatter

import app_utils
from water_modelling.metadata import metadata_dao
import weather_util
import json
import numpy as np
import os
import shutil
import local_configuration_dao as lcd


def create_project_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    name = request.json['name']
    lat = request.json['lat']
    long = request.json["long"]
    start_date = request.json["start_date"]
    end_date = request.json["end_date"]
    spin_up = request.json["spin_up"]

    # check for name collision
    lowercase_project_names = [name.lower() for name in metadata_dao.read_all()]
    if name.lower() in lowercase_project_names:
        return jsonify(error=str("A project with this name already exists (names are case-insensitive)")), 404

    project = ProjectMetadata(
        name=name,
        lat=lat,
        long=long,
        start_date=start_date,
        end_date=end_date,
        spin_up=spin_up)
    # # everything below here will be populated once modflow and hydrus models are loaded
    # "rows": None,
    # "cols": None,
    # "grid_unit": None,
    # "row_cells": [],
    # "col_cells": [],
    # "modflow_model": None,
    # "hydrus_models": []

    metadata_dao.create(project)
    state.reset_project_data()
    state.loaded_project = project
    return json.dumps({'status': 'OK'})


def get_projects(projects, offset=0, per_page=10):
    return projects[offset: offset + per_page]


def project_list_handler(search):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    project_names = metadata_dao.read_all()

    if search:
        project_names = [name for name in project_names if search.lower() in name.lower()]

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    pagination_projects = get_projects(projects=project_names, offset=offset, per_page=per_page)
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=len(project_names),
                            record_name="projects",
                            css_framework='bootstrap4')

    return render_template(template.PROJECT_LIST,
                           search_value=search,
                           projects=pagination_projects,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           error_project_name=state.get_error_flag()
                           )


def remove_project_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    body = json.loads(request.data)
    if body['projectName']:
        metadata_dao.remove_project(body['projectName'], state)
    return redirect(endpoints.PROJECT_LIST, code=303)


def project_handler(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    if project_name is None:
        # case 1 - there is already a project loaded and we just want to see it
        if state.loaded_project is not None:
            return render_template(template.PROJECT, project=state.loaded_project)
        # case 2 - there is no project loaded, the user should be redirected to the project list to select a project
        else:
            state.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)

    # case 3 - we're selecting a new project
    else:
        try:
            chosen_project = metadata_dao.read(project_name)

            # clear old data and load new project
            state.reset_project_data()
            state.loaded_project = chosen_project

            if state.loaded_project.modflow_model:
                model_path = os.path.join(state.get_modflow_dir(), state.loaded_project.modflow_model)
                nam_file_name = modflow_utils.get_nam_file(model_path)
                model_data = modflow_utils.get_model_data(model_path, nam_file_name)
                state.recharge_masks = modflow_utils.get_shapes_from_rch(
                    model_path, nam_file_name, (model_data["rows"], model_data["cols"])
                )

            return render_template(template.PROJECT, project=chosen_project)

        # case 3a - the project does not exist
        except FileNotFoundError:
            state.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)


def project_is_finished_handler(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    if project_name is not None:
        try:
            # Check if project exists
            metadata_dao.read(project_name)
        except FileNotFoundError:  # the project does not exist
            state.error_flag = True
            return redirect(endpoints.PROJECT_LIST)

        # TODO: Should be done by dao
        if os.path.exists(os.path.join(state.get_modflow_dir_by_project_name(project_name=project_name), "finished.0")):
            return json.dumps({'status': 'OK'})

    elif state.loaded_project is not None:
        if os.path.exists(os.path.join(state.get_modflow_dir(), "finished.0")):
            return json.dumps({'status': 'OK'})

    return json.dumps({'status': 'No Content'})


def project_download_handler(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    if project_name is not None:
        try:
            project = metadata_dao.read(project_name)
        except FileNotFoundError:  # the project does not exist
            state.error_flag = True
            return redirect(endpoints.PROJECT_LIST)
    else:
        project = state.loaded_project

    if project is not None:
        project_dir = os.path.join(deployment_config.WORKSPACE_DIR, project.name)
        zip_file = shutil.make_archive(project_dir, 'zip', project_dir)
        return send_file(zip_file, as_attachment=True)
    return '', 204


def edit_project_handler(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    try:
        project = metadata_dao.read(project_name)
        return render_template(
            template.CREATE_PROJECT,
            name=project_name,
            prev_lat=project.lat,
            prev_long=project.long,
            prev_start=project.start_date,
            prev_end=project.end_date,
            prev_spin_up=project.spin_up
        )
    except FileNotFoundError:
        state.activate_error_flag()
        return redirect(endpoints.PROJECT_LIST)


def update_project_settings():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    name = request.json['name']
    lat = request.json['lat']
    long = request.json["long"]
    start_date = request.json["start_date"]
    end_date = request.json["end_date"]
    spin_up = request.json['spin_up']

    try:
        project_metadata = metadata_dao.read(name)

        # Update metadata
        project_metadata.name = name
        project_metadata.lat = lat
        project_metadata.long = long
        project_metadata.start_date = start_date
        project_metadata.end_date = end_date
        project_metadata.spin_up = spin_up

        metadata_dao.save_or_update(project_metadata, state)
        return json.dumps({'status': 'OK'})

    except FileNotFoundError:
        state.activate_error_flag()
        return redirect(endpoints.PROJECT_LIST)


def upload_modflow_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    # every uploaded model needs to belong to a project;
    # if there is no active project, we cannot upload a model
    if state.loaded_project is None:
        return redirect(endpoints.PROJECT_LIST)

    model = request.files['archive-input']  # matches HTML input name
    filename = path_formatter.fix_model_name(model.filename)

    if state.type_allowed(model.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(state.get_modflow_dir(), filename)
        model.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the model name and remember it
            model_name = separate_model_name(filename)[0]

            # create a dedicated catalogue and load the model into it
            model_path = os.path.join(state.get_modflow_dir(), model_name)
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

        state.recharge_masks = modflow_utils.get_shapes_from_rch(model_path, nam_file_name,
                                                                 (model_data["rows"], model_data["cols"]))

        # update project JSON
        project_metadata = state.loaded_project
        project_metadata.modflow_model = model_name
        project_metadata.rows = model_data["rows"]
        project_metadata.cols = model_data["cols"]
        project_metadata.grid_unit = model_data["grid_unit"]
        project_metadata.row_cells = model_data["row_cells"]
        project_metadata.col_cells = model_data["col_cells"]

        metadata_dao.save_or_update(project_metadata, state)

        print("Modflow model uploaded successfully")  # TODO: Logger
        return redirect(endpoints.UPLOAD_MODFLOW)

    else:
        print("Invalid archive format, must be one of: ", end='')  # TODO: Logger
        print(deployment_config.ALLOWED_UPLOAD_TYPES)  # TODO: Logger
        return abort(500)


def upload_weather_file_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    # read data from request, sve file
    model_name = request.form['model_name']
    weather_file = request.files['file']
    filepath = os.path.join(state.get_hydrus_dir(), model_name, weather_file.filename)
    weather_file.save(filepath)

    # update hydrus project
    length_unit = metadata_dao.get_hydrus_length_unit(model_name, state)
    raw_data = weather_util.read_weather_csv(filepath)
    ready_data = weather_util.adapt_data(raw_data, length_unit)
    success = metadata_dao.add_weather_to_hydrus_model(model_name, ready_data, state)

    os.remove(filepath)

    if not success:
        return jsonify(error=str("Length mismatch between project data and file data")), 400

    return "Success", 200


def remove_modflow_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    body = json.loads(request.data)
    if body['modelName']:
        metadata_dao.remove_model(HydrologicalModelEnum.MODFLOW, body["modelName"], state)
    return redirect(endpoints.UPLOAD_MODFLOW, code=303)


def upload_hydrus_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    models = request.files.getlist('archive-input')

    error = None
    error_idx = 0
    start_count = len(state.loaded_project.hydrus_models)

    for i, model in enumerate(models):

        filename = path_formatter.fix_model_name(model.filename)
        if state.type_allowed(filename):
            model_name = separate_model_name(filename)[0]

            if model_name in state.loaded_project.hydrus_models:
                error_idx = i
                error = "Model with this name already exits: " + model_name
                break

            # save, unzip, remove archive
            archive_path = os.path.join(state.get_hydrus_dir(), filename)
            model.save(archive_path)

            with ZipFile(archive_path, 'r') as archive:
                # get the project name and remember it
                model_name = model.filename.split('.')[0]
                project_path = os.path.join(state.get_hydrus_dir(), model_name)

                # create a dedicated catalogue and load the project into it
                os.system('mkdir ' + project_path)
                archive.extractall(project_path)

                # validate model
                invalid_model = not hydrus_utils.validate_model(project_path)

            os.remove(archive_path)
            if invalid_model:
                error_idx = i
                error = "Invalid Hydrus project structure"
                shutil.rmtree(project_path, ignore_errors=True)
                break

            project_metadata = state.loaded_project
            project_metadata.hydrus_models.append(model_name)
            # update project JSON
            metadata_dao.save_or_update(project_metadata, state)

        else:
            error_idx = i
            error = "Invalid file type. Accepted types: " + ", ".join(deployment_config.ALLOWED_UPLOAD_TYPES)
            break

    if error is not None:
        for _ in range(error_idx):
            model_name = state.loaded_project.hydrus_models.pop(start_count)

            shutil.rmtree(os.path.join(state.get_hydrus_dir(), model_name),
                          ignore_errors=True)  # remove invalid project dir

        print(error)  # TODO: Logger
        return jsonify(error=error), 500

    print("Hydrus model uploaded successfully")  # TODO: Logger
    return redirect(endpoints.UPLOAD_HYDRUS)


def separate_model_name(filename: str) -> Tuple[str, str]:
    """
    Separates filename and its extension
    @param filename: name of the file including the extension
    @return: Tuple of 2 strings: (name of the file, extension)
    """
    split = filename.split('.')
    return '.'.join(split[:-1]), split[-1]


def remove_hydrus_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    body = json.loads(request.data)
    hydrus_model_name = body['modelName']

    print("received call")  # TODO: Logger
    print(hydrus_model_name)  # TODO: Logger

    if hydrus_model_name:
        metadata_dao.remove_model(HydrologicalModelEnum.HYDRUS, hydrus_model_name, state)
        if hydrus_model_name in state.loaded_shapes.keys():
            del state.loaded_shapes[hydrus_model_name]
        if hydrus_model_name in state.models_masks_ids.keys():
            del state.models_masks_ids[hydrus_model_name]
    return redirect(endpoints.UPLOAD_HYDRUS, code=303)


def upload_shape_handler(req, hydrus_model_index):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    # if not yet done, initialize the shape arrays list to the amount of models
    if len(state.loaded_shapes) < len(state.loaded_project.hydrus_models):
        for hydrus_model in state.loaded_project.hydrus_models:
            state.loaded_shapes[hydrus_model] = None

    # read the array from the request and store it
    hydrus_model = state.loaded_project.hydrus_models[hydrus_model_index]
    shape_array = np.array(req.get_json(force=True))
    shape_metadata = ShapeMetadata(shape_array, state.loaded_project.name, hydrus_model)
    state.loaded_shapes[hydrus_model] = shape_metadata

    daos.mask_dao.save_or_update(shape_metadata)
    return json.dumps({'status': 'OK'})


def next_model_redirect_handler(hydrus_model_index, error_flag):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    # check if we still have models to go, if not, redirect to next section
    if hydrus_model_index >= len(state.loaded_project.hydrus_models):
        for key in state.loaded_shapes:
            print(key, '->\n', state.loaded_shapes[key].shape_mask)  # TODO: Logger
        return redirect(endpoints.SIMULATION)

    else:
        rows_height, cols_width = modflow_utils.scale_cells_size(state.loaded_project.row_cells,
                                                                 state.loaded_project.col_cells, 500)
        return render_template(
            template.DEFINE_SHAPES,
            rowAmount=state.loaded_project.rows,
            colAmount=state.loaded_project.cols,
            rows=[str(x) for x in range(state.loaded_project.rows)],
            cols=[str(x) for x in range(state.loaded_project.cols)],
            cols_width=cols_width,
            rows_height=rows_height,
            modelIndex=hydrus_model_index,
            modelName=state.loaded_project.hydrus_models[hydrus_model_index],
            upload_error=error_flag
        )


def next_shape_redirect_handler(rch_shape_index: int):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    if rch_shape_index >= len(state.recharge_masks):
        state.get_shapes_from_masks_ids()
        for key in state.loaded_shapes:
            print(key, '->\n', state.loaded_shapes[key].shape_mask)  # TODO: Logger
        return redirect(endpoints.SIMULATION)
    else:
        current_model = state.get_current_model_by_id(rch_shape_index)
        rows_height, cols_width = modflow_utils.scale_cells_size(state.loaded_project.row_cells,
                                                                 state.loaded_project.col_cells, 500)
        return render_template(template.RCH_SHAPES, hydrus_models=state.loaded_project.hydrus_models,
                               shape_mask=state.recharge_masks[rch_shape_index], rch_shape_index=rch_shape_index,
                               rows_height=rows_height, cols_width=cols_width, current_model=current_model)


def assign_model_to_shape(req, rch_shape_index):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    hydrus_model_name = req.json["hydrusModel"]
    previous_hydrus_model_name = req.json["previousModel"]

    if previous_hydrus_model_name:
        state.models_masks_ids[previous_hydrus_model_name].remove(rch_shape_index)

    if hydrus_model_name == "":
        return json.dumps({'status': 'OK'})

    if hydrus_model_name not in state.models_masks_ids or state.models_masks_ids[hydrus_model_name] is None:
        state.loaded_shapes[hydrus_model_name] = None
        state.models_masks_ids[hydrus_model_name] = [rch_shape_index]
    else:
        state.models_masks_ids[hydrus_model_name].append(rch_shape_index)

    return json.dumps({'status': 'OK'})


def upload_new_configurations():
    modflow_exe = request.json['modflowExe']
    hydrus_exe = request.json['hydrusExe']

    if not os.path.exists(modflow_exe):
        return jsonify(error=str("Incorrect Modflow exe path"), model=str("modflow")), 404

    if not os.path.exists(hydrus_exe):
        return jsonify(error=str("Incorrect Hydrus exe path"), model=str("hydrus")), 404

    lcd.update_configuration(hydrus_exe, modflow_exe)

    return json.dumps({'status': 'OK'})


def simulation_summary_handler():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))

    rows_height, cols_width = modflow_utils.scale_cells_size(state.loaded_project.row_cells,
                                                             state.loaded_project.col_cells, 500)

    return render_template(
        template.SIMULATION,
        modflow_proj=state.loaded_project.modflow_model,
        shapes=state.loaded_shapes,
        cols_width=cols_width,
        rows_height=rows_height,
    )
