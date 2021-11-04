from app_utils import AppUtils
import numpy as np
from flask import render_template, redirect, abort
from zipfile import ZipFile
from datapassing.shape_data import ShapeFileData
from DAO import DAO, PROJECTS, RESULTS
from constants import DB_URL
import shutil

import os
import json

from modflow import modflow_utils
from server import endpoints, template

util = AppUtils()
util.setup()

dao = DAO(DB_URL)


def project_list_handler():
    return render_template(template.PROJECT_LIST, projects=dao.read_all(PROJECTS))


def upload_modflow_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.modflow_dir, project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the project name and remember it
            project_name = project.filename.split('.')[0]

            # create a dedicated catalogue and load the project into it
            project_path = os.path.join(util.modflow_dir, project_name)
            os.system('mkdir ' + project_path)
            archive.extractall(project_path)

            # validate model
            util.nam_file_name = modflow_utils.get_nam_file(project_path)
            invalid_model = not modflow_utils.validate_model(project_path, util.nam_file_name)

        os.remove(archive_path)
        if invalid_model:
            shutil.rmtree(project_path, ignore_errors=True)  # remove invalid project dir
            return abort(500)

        util.modflow_rows, util.modflow_cols = modflow_utils.get_model_size(project_path, util.nam_file_name)
        util.recharge_masks = modflow_utils.get_shapes_from_rch(project_path, util.nam_file_name,
                                                                (util.modflow_rows, util.modflow_cols))
        util.loaded_modflow_models = [project_name]
        print("Project uploaded successfully")
        return redirect(endpoints.UPLOAD_MODFLOW)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return abort(500)


def upload_hydrus_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.hydrus_dir, project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_hydrus_models.append(project_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.hydrus_dir, project_name))
            archive.extractall(os.path.join(util.hydrus_dir, project_name))

        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(endpoints.UPLOAD_HYDRUS)

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_shape_handler(req, hydrus_model_index):
    # if not yet done, initialize the shape arrays list to the amount of models
    if len(util.loaded_shapes) < len(util.loaded_hydrus_models):

        for hydrus_model in util.loaded_hydrus_models:
            util.loaded_shapes[hydrus_model] = None
        # util.loaded_shapes = [None for _ in range(len(util.loaded_hydrus_models))]

    # read the array from the request and store it
    shape_array = req.get_json(force=True)
    np_array_shape = np.array(shape_array)
    util.loaded_shapes[util.loaded_hydrus_models[hydrus_model_index]] = ShapeFileData(shape_mask_array=np_array_shape)

    return json.dumps({'status': 'OK'})


def next_model_redirect_handler(hydrus_model_index, error_flag):
    # check if we still have models to go, if not, redirect to next section
    if hydrus_model_index >= len(util.loaded_hydrus_models):
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
            modelName=util.loaded_hydrus_models[hydrus_model_index],
            upload_error=error_flag
        )
