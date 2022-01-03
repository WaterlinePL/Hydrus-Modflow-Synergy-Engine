from typing import Optional

from flask import Response, redirect

from server import endpoints
from server.user_state import UserState


def path_check_cookie(state: UserState) -> Optional[Response]:
    """
    @param state: UserState containing current state of application.
    @return: Optional redirect to main page with getting cookie.
    """

    if not state:
        return redirect(endpoints.HOME)
    return None


def path_check_simulate_access(state: UserState) -> Optional[Response]:
    """
    @param state: UserState containing current state of application.
    @return: Optional redirect to configuration if no paths for Hydrus and Modflow are specified.
    """

    check_previous = path_check_cookie(state)
    if check_previous:
        return check_previous

    return None


def path_check_modflow_step(state: UserState) -> Optional[Response]:
    """
    @param state: UserState containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_modflow (first step).
    """

    check_previous = path_check_simulate_access(state)
    if check_previous:
        return check_previous

    if state.get_modflow_dir() is None or not state.loaded_project["modflow_model"]:
        state.activate_error_flag()
        return redirect(endpoints.UPLOAD_MODFLOW)

    return None


def path_check_hydrus_step(state: UserState) -> Optional[Response]:
    """
    @param state: UserState containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_hydrus.
    """

    check_previous = path_check_modflow_step(state)
    if check_previous:
        return check_previous

    # TODO: check if Hydrus step was visited? (upload of projects is not mandatory)
    if state.get_hydrus_dir() is None or not state.loaded_project["hydrus_models"]:
        state.activate_error_flag()
        return redirect(endpoints.UPLOAD_HYDRUS)

    return None


def path_check_define_shapes_method(state: UserState) -> Optional[Response]:
    """
    @param state: UserState containing current state of application.
    @return: Optional redirect to first incorrect step up to define_method.
    """

    check_previous = path_check_hydrus_step(state)
    if check_previous:
        return check_previous

    if state.current_method is None or state.loaded_shapes is None:
        # redirect to define method page if method was not selected
        state.activate_error_flag()
        return redirect(endpoints.DEFINE_METHOD)

    for hydrus_model in state.loaded_project["hydrus_models"]:
        if hydrus_model not in state.loaded_shapes.keys():
            state.loaded_shapes[hydrus_model] = state.create_empty_mask()

    return None


# used in url_for(), requires base address of endpoint (for future)
def _format_endpoint_to_url(endpoint: str):
    return endpoint[1:].replace('-', '_')
