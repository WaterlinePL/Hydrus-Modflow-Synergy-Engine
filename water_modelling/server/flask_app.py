from flask import Flask, render_template, request, redirect, jsonify

import endpoint_handlers
from server import endpoints, template, path_checker
from simulation.simulation_service import SimulationService
import threading

util = endpoint_handlers.util
app = Flask("App")
simulation_service = None  # TODO - create SimulationService instance once a project has been loaded (how?)


# ------------------- ROUTES -------------------
@app.route('/')
def start():
    return redirect(endpoints.HOME)


@app.route(endpoints.HOME, methods=['GET'])
def home():
    return render_template(template.HOME)


@app.route(endpoints.PROJECT_LIST, methods=['GET'])
def project_list():
    return endpoint_handlers.project_list_handler()


@app.route(endpoints.PROJECT, methods=['GET'])
@app.route(endpoints.PROJECT_NO_ID, defaults={'project_name': None})
def project(project_name):
    return endpoint_handlers.project_handler(project_name)


@app.route(endpoints.UPLOAD_MODFLOW, methods=['GET', 'POST'])
def upload_modflow():
    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_modflow_handler(request)
    else:
        return render_template(template.UPLOAD_MODFLOW,
                               model_names=util.loaded_modflow_models,
                               upload_error=util.get_error_flag())


@app.route(endpoints.UPLOAD_HYDRUS, methods=['GET', 'POST'])
def upload_hydrus():
    check_previous_steps = path_checker.path_check_modflow_step(util)
    if check_previous_steps:
        return check_previous_steps
    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_hydrus_handler(request)
    else:
        return render_template(template.UPLOAD_HYDRUS,
                               model_names=util.loaded_hydrus_models,
                               upload_error=util.get_error_flag())


@app.route(endpoints.DEFINE_SHAPES, methods=['GET', 'POST'])
def define_shapes(hydrus_model_index):
    check_previous_steps = path_checker.path_check_hydrus_step(util)
    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST':
        return endpoint_handlers.upload_shape_handler(request, int(hydrus_model_index))
    else:
        return endpoint_handlers.next_model_redirect_handler(int(hydrus_model_index), util.get_error_flag())


@app.route(endpoints.SIMULATION, methods=['GET'])
def simulation():
    check_previous_steps = path_checker.path_check_define_shapes(util)
    if check_previous_steps:
        return check_previous_steps

    return render_template(template.SIMULATION, modflow_proj=util.loaded_modflow_models, shapes=util.loaded_shapes)


@app.route(endpoints.SIMULATION_RUN)
def run_simulation():
    check_previous_steps = path_checker.path_check_define_shapes(util)
    if check_previous_steps:
        return check_previous_steps

    sim = simulation_service.prepare_simulation()

    sim.set_modflow_project(modflow_project=util.loaded_modflow_models[0])
    sim.set_loaded_shapes(loaded_shapes=util.loaded_shapes)

    sim_id = sim.get_id()

    thread = threading.Thread(target=simulation_service.run_simulation, args=(sim_id, "default"))
    thread.start()
    return jsonify(id=sim_id)


@app.route(endpoints.SIMULATION_CHECK, methods=['GET'])
def check_simulation_status(simulation_id: int):
    hydrus_finished, passing_finished, modflow_finished = simulation_service.check_simulation_status(int(simulation_id))
    response = {'hydrus': hydrus_finished, 'passing': passing_finished, 'modflow': modflow_finished}
    return jsonify(response)
