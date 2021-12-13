from flask import Flask, render_template, request, redirect, jsonify
from server import endpoints, template, path_checker

from app_utils import util
import threading
import endpoint_handlers
import local_configuration_dao as lcd
from simulation.simulation_service import SimulationService

app = Flask("App")


# ------------------- ROUTES -------------------
@app.route('/')
def start():
    return redirect(endpoints.HOME)


@app.route(endpoints.HOME, methods=['GET'])
def home():
    return render_template(template.HOME)


@app.route(endpoints.CONFIGURATION, methods=['GET', 'POST'])
def configuration():
    if request.method == 'POST':
        return endpoint_handlers.upload_new_configurations(request)
    else:
        config = lcd.read_configuration()
        return render_template(template.CONFIGURATION,
                               modflow_exe=config["modflow_exe"],
                               hydrus_exe=config["hydrus_exe"],
                               paths_incorrect=util.get_error_flag())


@app.route(endpoints.CREATE_PROJECT, methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        return endpoint_handlers.create_project_handler(request)
    else:
        return render_template(template.CREATE_PROJECT)


@app.route(endpoints.EDIT_PROJECT, methods=['GET', 'POST'])
def edit_project(project_name):
    if request.method == 'POST':
        return endpoint_handlers.update_project_settings(request)
    else:
        return endpoint_handlers.edit_project_handler(project_name)


@app.route(endpoints.PROJECT_LIST, methods=['GET', 'DELETE'], defaults={'search': None})
@app.route(endpoints.PROJECT_LIST_SEARCH)
def project_list(search):
    if request.method == 'GET':
        return endpoint_handlers.project_list_handler(search)
    else:
        return endpoint_handlers.remove_project_handler(request)


@app.route(endpoints.PROJECT, methods=['GET'])
@app.route(endpoints.PROJECT_NO_ID, defaults={'project_name': None})
def project(project_name):
    return endpoint_handlers.project_handler(project_name)


@app.route(endpoints.PROJECT_FINISHED, methods=['GET'])
@app.route(endpoints.PROJECT_FINISHED_NO_ID, defaults={'project_name': None})
def project_is_finished(project_name):
    return endpoint_handlers.project_is_finished_handler(project_name)


@app.route(endpoints.PROJECT_DOWNLOAD, methods=['GET'])
@app.route(endpoints.PROJECT_DOWNLOAD_NO_ID, defaults={'project_name': None})
def project_download(project_name):
    return endpoint_handlers.project_download_handler(project_name)


@app.route(endpoints.UPLOAD_MODFLOW, methods=['GET', 'POST', 'DELETE'])
def upload_modflow():
    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_modflow_handler(request)
    elif request.method == 'DELETE':
        return endpoint_handlers.remove_modflow_handler(request)
    else:
        if util.loaded_project is None:
            util.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)
        else:
            check_previous_steps = path_checker.path_check_simulate_access(util)
            if check_previous_steps:
                return check_previous_steps

            return render_template(
                template.UPLOAD_MODFLOW,
                model_name=util.loaded_project["modflow_model"],
                upload_error=util.get_error_flag()
            )


@app.route(endpoints.UPLOAD_WEATHER_FILE, methods=['GET', 'POST'])
def upload_weather_file():
    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_weather_file_handler(request)
    else:  # GET
        if util.loaded_project is not None:
            return render_template(
                template.UPLOAD_WEATHER_FILE,
                hydrus_models=util.loaded_project["hydrus_models"],
                upload_error=False
            )
        else:
            util.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)


@app.route(endpoints.UPLOAD_HYDRUS, methods=['GET', 'POST', 'DELETE'])
def upload_hydrus():
    check_previous_steps = path_checker.path_check_modflow_step(util)
    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_hydrus_handler(request)
    elif request.method == 'DELETE':
        return endpoint_handlers.remove_hydrus_handler(request)
    else:
        return render_template(template.UPLOAD_HYDRUS,
                               model_names=util.loaded_project["hydrus_models"],
                               upload_error=util.get_error_flag())


@app.route(endpoints.DEFINE_METHOD, methods=['GET'])
def define_method():
    check_previous_steps = path_checker.path_check_hydrus_step(util)
    if check_previous_steps:
        return check_previous_steps

    return render_template(template.DEFINE_METHOD, error=util.get_error_flag())


@app.route(endpoints.MANUAL_SHAPES, methods=['GET', 'POST'])
def manual_shapes(hydrus_model_index):
    check_previous_steps = path_checker.path_check_hydrus_step(util)
    if check_previous_steps:
        return check_previous_steps

    util.set_method(endpoints.MANUAL_SHAPES)

    if request.method == 'POST':
        return endpoint_handlers.upload_shape_handler(request, int(hydrus_model_index))
    else:
        return endpoint_handlers.next_model_redirect_handler(int(hydrus_model_index), util.get_error_flag())


@app.route(endpoints.RCH_SHAPES, methods=['GET', 'POST'])
def rch_shapes(rch_shape_index):
    check_previous_steps = path_checker.path_check_hydrus_step(util)
    if check_previous_steps:
        return check_previous_steps

    util.set_method(endpoints.RCH_SHAPES)

    if request.method == 'POST':
        return endpoint_handlers.assign_model_to_shape(request, int(rch_shape_index))
    else:
        return endpoint_handlers.next_shape_redirect_handler(int(rch_shape_index))


@app.route(endpoints.SIMULATION, methods=['GET'])
def simulation():
    check_previous_steps = path_checker.path_check_define_shapes_method(util)
    if check_previous_steps:
        return check_previous_steps

    return endpoint_handlers.simulation_summary_handler()


@app.route(endpoints.SIMULATION_RUN)
def run_simulation():
    check_previous_steps = path_checker.path_check_define_shapes_method(util)
    if check_previous_steps:
        return check_previous_steps

    if util.loaded_project is not None:
        simulation_service = SimulationService(util.get_hydrus_dir(), util.get_modflow_dir())

    util.set_simulation_serivce(simulation_service)
    sim = util.simulation_service.prepare_simulation()

    sim.set_modflow_project(modflow_project=util.loaded_project["modflow_model"])
    sim.set_loaded_shapes(loaded_shapes=util.loaded_shapes)
    sim.set_spin_up(spin_up=int(util.loaded_project["spin_up"]))

    sim_id = sim.get_id()

    thread = threading.Thread(target=util.simulation_service.run_simulation, args=[sim_id])
    thread.start()
    return jsonify(id=sim_id)


@app.route(endpoints.SIMULATION_CHECK, methods=['GET'])
def check_simulation_status(simulation_id: int):
    hydrus_finished, passing_finished, modflow_finished = util.simulation_service.check_simulation_status(
        int(simulation_id))
    response = {'hydrus': hydrus_finished, 'passing': passing_finished, 'modflow': modflow_finished}
    return jsonify(response)
