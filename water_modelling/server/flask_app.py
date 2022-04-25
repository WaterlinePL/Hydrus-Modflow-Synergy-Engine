import uuid

from flask import Flask, render_template, request, redirect, jsonify, make_response
from server import endpoints, template, path_checker
import app_utils
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
    res = make_response(render_template(template.HOME))
    if not request.cookies.get(app_utils.COOKIE_NAME):
        cookie = str(uuid.uuid4())
        res.set_cookie(app_utils.COOKIE_NAME, cookie, max_age=60 * 60 * 24 * 365 * 2)
        app_utils.add_user(cookie)
    return res


@app.route(endpoints.CONFIGURATION, methods=['GET', 'POST'])
def configuration():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST':
        return endpoint_handlers.upload_new_configurations()
    else:
        config = lcd.read_configuration()
        return render_template(template.CONFIGURATION,
                               modflow_exe=config["modflow_exe"],
                               hydrus_exe=config["hydrus_exe"],
                               paths_incorrect=state.get_error_flag())


@app.route(endpoints.CREATE_PROJECT, methods=['GET', 'POST'])
def create_project():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST':
        return endpoint_handlers.create_project_handler()
    else:
        return render_template(template.CREATE_PROJECT)


@app.route(endpoints.EDIT_PROJECT, methods=['GET', 'POST'])
def edit_project(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST':
        return endpoint_handlers.update_project_settings()
    else:
        return endpoint_handlers.edit_project_handler(project_name)


@app.route(endpoints.PROJECT_LIST, methods=['GET', 'DELETE'], defaults={'search': None})
@app.route(endpoints.PROJECT_LIST_SEARCH)
def project_list(search):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'GET':
        return endpoint_handlers.project_list_handler(search)
    else:
        return endpoint_handlers.remove_project_handler()


@app.route(endpoints.PROJECT, methods=['GET'])
@app.route(endpoints.PROJECT_NO_ID, defaults={'project_name': None})
def project(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    return endpoint_handlers.project_handler(project_name)


@app.route(endpoints.PROJECT_FINISHED, methods=['GET'])
@app.route(endpoints.PROJECT_FINISHED_NO_ID, defaults={'project_name': None})
def project_is_finished(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    return endpoint_handlers.project_is_finished_handler(project_name)


@app.route(endpoints.PROJECT_DOWNLOAD, methods=['GET'])
@app.route(endpoints.PROJECT_DOWNLOAD_NO_ID, defaults={'project_name': None})
def project_download(project_name):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    return endpoint_handlers.project_download_handler(project_name)


@app.route(endpoints.UPLOAD_MODFLOW, methods=['GET', 'POST', 'DELETE'])
def upload_modflow():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_modflow_handler()
    elif request.method == 'DELETE':
        return endpoint_handlers.remove_modflow_handler()
    else:
        if state.loaded_project is None:
            state.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)
        else:
            check_previous_steps = path_checker.path_check_simulate_access(state)
            if check_previous_steps:
                return check_previous_steps

            return render_template(
                template.UPLOAD_MODFLOW,
                model_name=state.loaded_project.modflow_model,
                upload_error=state.get_error_flag()
            )


@app.route(endpoints.UPLOAD_WEATHER_FILE, methods=['GET', 'POST'])
def upload_weather_file():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_cookie(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_weather_file_handler()
    else:  # GET
        if state.loaded_project is not None:
            return render_template(
                template.UPLOAD_WEATHER_FILE,
                hydrus_models=state.loaded_project.hydrus_models,
                upload_error=False
            )
        else:
            state.activate_error_flag()
            return redirect(endpoints.PROJECT_LIST)


@app.route(endpoints.UPLOAD_HYDRUS, methods=['GET', 'POST', 'DELETE'])
def upload_hydrus():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_modflow_step(state)

    if check_previous_steps:
        return check_previous_steps

    if request.method == 'POST' and request.files:
        return endpoint_handlers.upload_hydrus_handler()
    elif request.method == 'DELETE':
        return endpoint_handlers.remove_hydrus_handler()
    else:
        return render_template(template.UPLOAD_HYDRUS,
                               model_names=state.loaded_project.hydrus_models,
                               upload_error=state.get_error_flag())


@app.route(endpoints.DEFINE_METHOD, methods=['GET'])
def define_method():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_hydrus_step(state)

    if check_previous_steps:
        return check_previous_steps

    return render_template(template.DEFINE_METHOD, error=state.get_error_flag())


@app.route(endpoints.MANUAL_SHAPES, methods=['GET', 'POST'])
def manual_shapes(hydrus_model_index):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_hydrus_step(state)

    if check_previous_steps:
        return check_previous_steps

    state.set_method(endpoints.MANUAL_SHAPES)

    if request.method == 'POST':
        return endpoint_handlers.upload_shape_handler(request, int(hydrus_model_index))
    else:
        return endpoint_handlers.next_model_redirect_handler(int(hydrus_model_index), state.get_error_flag())


@app.route(endpoints.RCH_SHAPES, methods=['GET', 'POST'])
def rch_shapes(rch_shape_index):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_hydrus_step(state)

    if check_previous_steps:
        return check_previous_steps

    state.set_method(endpoints.RCH_SHAPES)

    if request.method == 'POST':
        return endpoint_handlers.assign_model_to_shape(request, int(rch_shape_index))
    else:
        return endpoint_handlers.next_shape_redirect_handler(int(rch_shape_index))


@app.route(endpoints.SIMULATION, methods=['GET'])
def simulation():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_define_shapes_method(state)

    if check_previous_steps:
        return check_previous_steps

    return endpoint_handlers.simulation_summary_handler()


@app.route(endpoints.SIMULATION_RUN)
def run_simulation():
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    check_previous_steps = path_checker.path_check_define_shapes_method(state)
    if check_previous_steps:
        return check_previous_steps

    simulation_service = SimulationService(state.get_hydrus_dir(), state.get_modflow_dir())
    state.set_simulation_service(simulation_service)
    sim = state.simulation_service.prepare_simulation()

    sim.set_modflow_project(modflow_project=state.loaded_project.modflow_model)
    sim.set_loaded_shapes(loaded_shapes=state.loaded_shapes)
    sim.set_spin_up(spin_up=int(state.loaded_project.spin_up))

    sim_id = sim.get_id()

    thread = threading.Thread(target=state.simulation_service.run_simulation, args=[sim_id])
    thread.start()
    return jsonify(id=sim_id)


@app.route(endpoints.SIMULATION_CHECK, methods=['GET'])
def check_simulation_status(simulation_id: int):
    state = app_utils.get_user_by_cookie(request.cookies.get(app_utils.COOKIE_NAME))
    hydrus_stage_status, passing_stage_status, modflow_stage_status = state.simulation_service.check_simulation_status(
        int(simulation_id))

    response = {
        'hydrus': {
            'finished': hydrus_stage_status.has_ended(),
            'errors': [str(sim_error) for sim_error in hydrus_stage_status.get_errors()]
        },
        'passing': {
            'finished': passing_stage_status.has_ended(),
            'errors': [str(sim_error) for sim_error in passing_stage_status.get_errors()]
        },
        'modflow': {
            'finished': modflow_stage_status.has_ended(),
            'errors': [str(sim_error) for sim_error in modflow_stage_status.get_errors()]
        }
    }

    return jsonify(response)
