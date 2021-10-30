import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from zipfile import ZipFile
from datapassing.shapeData import ShapeFileData, Shape
from DAO import DAO, PROJECTS, RESULTS
from constants import DB_URL
import shutil
import flopy

import os
import json

from AppUtils import AppUtils
from simulation.SimulationService import SimulationService
import threading

util = AppUtils()
util.setup()

dao = DAO(DB_URL)

app = Flask("App")
simulation_service = SimulationService(hydrus_dir=util.hydrus_dir,
                                       modflow_dir=util.modflow_dir)


# ------------------- ROUTES -------------------
@app.route('/')
def start():
    return redirect(request.url + "home")


@app.route('/upload-modflow', methods=['GET', 'POST'])
def upload_modflow():
    error_flag = util.error_flag
    util.error_flag = False

    if request.method == 'POST' and request.files:
        return upload_modflow_handler(request)
    else:
        return render_template('uploadModflow.html', model_names=util.loaded_modflow_models, upload_error=error_flag)


@app.route('/upload-hydrus', methods=['GET', 'POST'])
def upload_hydrus():
    is_path_correct = path_check(hydrus_path=True)
    if is_path_correct is not True:
        return is_path_correct

    error_flag = util.error_flag
    util.error_flag = False

    if request.method == 'POST' and request.files:
        return upload_hydrus_handler(request)
    else:
        return render_template('uploadHydrus.html', model_names=util.loaded_hydrus_models, upload_error=error_flag)


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/define-shapes/<hydrus_model_index>', methods=['GET', 'POST'])
def define_shapes(hydrus_model_index):
    is_path_correct = path_check(shapes_path=True)
    if is_path_correct is not True:
        return is_path_correct

    error_flag = util.error_flag
    util.error_flag = False

    if request.method == 'POST':
        return upload_shape_handler(request, int(hydrus_model_index))
    else:
        return next_model_redirect_handler(int(hydrus_model_index), error_flag)


@app.route('/simulation', methods=['GET'])
def simulation():
    is_path_correct = path_check()
    if is_path_correct is not True:
        return is_path_correct
    return render_template('simulation.html', modflow_proj=util.loaded_modflow_models,
                           shapes=util.loaded_shapes)


@app.route('/simulation-run')
def run_simulation():
    is_path_correct = path_check()
    if is_path_correct is not True:
        return is_path_correct

    sim = simulation_service.prepare_simulation()

    sim.set_modflow_project(modflow_project=util.loaded_modflow_models[0])
    sim.set_loaded_shapes(loaded_shapes=util.loaded_shapes)

    sim_id = sim.get_id()

    thread = threading.Thread(target=simulation_service.run_simulation, args=(sim_id, "default"))
    thread.start()
    return jsonify(id=sim_id)


@app.route('/simulation-check/<simulation_id>', methods=['GET'])
def check_simulation_status(simulation_id: int):
    hydrus_finished, passing_finished, modflow_finished = simulation_service.check_simulation_status(int(simulation_id))
    response = {'hydrus': hydrus_finished, 'passing': passing_finished, 'modflow': modflow_finished}
    return jsonify(response)


# ------------------- END ROUTES -------------------

def path_check(hydrus_path: bool = False, shapes_path: bool = False):
    '''
    :param hydrus_path: True if we use path_check() function trying to access upload-hydrus page
    :param shapes_path: True if we use path_check() function trying to access define-shapes page
    :return: True if user is authorized to access chosen page. Otherwise user is
             redirected to correct page (for example to upload missing model).
    '''
    if util.modflow_dir is None or not util.loaded_modflow_models:
        # redirect to upload modflow page if model is not defined
        util.error_flag = True
        return redirect(url_for('upload_modflow'))
    elif hydrus_path is False and (util.hydrus_dir is None or not util.loaded_hydrus_models):
        # redirect to upload hydrus page if model is not defined
        util.error_flag = True
        return redirect(url_for('upload_hydrus'))
    elif (hydrus_path is False and shapes_path is False) and (not util.loaded_shapes):
        # redirect to define shapes page if shapes are not defined
        util.error_flag = True
        return redirect(url_for('define_shapes', hydrus_model_index=0))
    return True


# ------------------- HANDLERS -------------------

def upload_modflow_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'modflow', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the project name and remember it
            project_name = project.filename.split('.')[0]

            # create a dedicated catalogue and load the project into it
            project_path = os.path.join(util.workspace_dir, 'modflow', project_name)
            os.system('mkdir ' + project_path)
            archive.extractall(project_path)

            # validate model
            invalid_model = not is_modflow_model_valid(project_path)

        os.remove(archive_path)
        if invalid_model:
            shutil.rmtree(project_path, ignore_errors=True)  # remove invalid project dir
            return abort(500)

        get_model_size(project_path)
        get_shapes_from_rch(project_path)
        util.loaded_modflow_models = [project_name]
        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-modflow')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return abort(500)


def upload_hydrus_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'hydrus', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_hydrus_models.append(project_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.workspace_dir, 'hydrus', project_name))
            archive.extractall(os.path.join(util.workspace_dir, 'hydrus', project_name))

        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-hydrus')

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
        return redirect(url_for('simulation'))

    else:
        return render_template(
            'defineShapes.html',
            rowAmount=util.modflow_rows,
            colAmount=util.modflow_cols,
            rows=[str(x) for x in range(util.modflow_rows)],
            cols=[str(x) for x in range(util.modflow_cols)],
            modelIndex=hydrus_model_index,
            modelName=util.loaded_hydrus_models[hydrus_model_index],
            upload_error=error_flag
        )


# ------------------- END HANDLERS -------------------


# ------------------- MISC FUNCTIONS -------------------

def get_nam_file(project_path: str) -> None:
    for filename in os.listdir(project_path):
        filename = str(filename)
        if filename.endswith(".nam"):
            util.nam_file_name = filename
            return
    print("ERROR: invalid modflow model; missing .nam file")


def is_modflow_model_valid(project_path: str) -> bool:
    get_nam_file(project_path)
    if not util.nam_file_name:
        return False
    try:
        # load whole model and validate it
        m = flopy.modflow.Modflow.load(util.nam_file_name, model_ws=project_path, forgive=True, check=True)
        if m.rch is None:
            print("Model doesn't contain .rch file")
            return False
        m.rch.check()
    except IOError:
        print("Model is not valid - files are missing")
        return False
    except KeyError:
        print("Model is not valid - modflow common error")
        return False

    return True


def get_model_size(project_path: str) -> None:
    modflow_model = flopy.modflow.Modflow \
        .load(util.nam_file_name, model_ws=project_path, load_only=["rch"], forgive=True)
    util.modflow_rows = modflow_model.nrow
    util.modflow_cols = modflow_model.ncol


def get_shapes_from_rch(project_path: str) -> None:
    """
    Defines shapes masks for uploaded modflow model based on recharge
    @param project_path: path to modflow project main directory
    @return: None
    """
    modflow_model = flopy.modflow.Modflow \
        .load(util.nam_file_name, model_ws=project_path, load_only=["rch"], forgive=True)

    stress_period = 0
    layer = 0

    util.recharge_masks = []
    is_checked_array = np.full((util.modflow_rows, util.modflow_cols), False)
    recharge_array = modflow_model.rch.rech.array[stress_period][layer]

    for i in range(util.modflow_rows):
        for j in range(util.modflow_cols):
            if not is_checked_array[i][j]:
                util.recharge_masks.append(np.zeros((util.modflow_rows, util.modflow_cols)))
                fill_mask_recursive(mask=util.recharge_masks[-1], recharge_array=recharge_array,
                                    is_checked_array=is_checked_array, i=i, j=j, value=recharge_array[i][j])

    print(util.recharge_masks)


def fill_mask_recursive(mask, recharge_array, is_checked_array, i: int, j: int, value: float):
    """
    Fill given mask with 1's according to recharge array
    @param mask: Binary mask of current shape - initially filled with 0's
    @param recharge_array: 2d array filled with modflow model recharge values
    @param is_checked_array: control array - 'True' means that given cell was already used in one of the masks
    @param i: column index
    @param j: row index
    @param value: recharge value of current mask
    @return: None
    """
    # return condition - out of bounds or given cell was already used
    if i < 0 or i >= util.modflow_rows or j < 0 or j >= util.modflow_cols or is_checked_array[i][j]:
        return
    if recharge_array[i][j] == value:
        is_checked_array[i][j] = True
        mask[i][j] = 1
        fill_mask_recursive(mask, recharge_array, is_checked_array, i - 1, j, value)
        fill_mask_recursive(mask, recharge_array, is_checked_array, i + 1, j, value)
        fill_mask_recursive(mask, recharge_array, is_checked_array, i, j - 1, value)
        fill_mask_recursive(mask, recharge_array, is_checked_array, i, j + 1, value)
    return

# ------------------- END MISC FUNCTIONS -------------------
