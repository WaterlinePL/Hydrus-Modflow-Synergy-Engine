from typing import Optional

from flask import Response, redirect, url_for

from server import endpoints
from server.app_utils import AppUtils
import server.local_configuration_dao as lcd


def path_check_simulate_access(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to configuration if no paths for Hydrus and Modflow are specified.
    """

    # TODO: add some condition if its a local version
    if not lcd.read_configuration()["modflow_exe"] or not lcd.read_configuration()["hydrus_exe"]:
        util.activate_error_flag()
        return redirect(endpoints.CONFIGURATION)

    return None


def path_check_modflow_step(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_modflow (first step).
    """

    check_previous = path_check_simulate_access(util)
    if check_previous:
        return check_previous

    if util.get_modflow_dir() is None or not util.loaded_project["modflow_model"]:
        util.activate_error_flag()
        return redirect(endpoints.UPLOAD_MODFLOW)

    return None


def path_check_hydrus_step(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_hydrus.
    """

    check_previous = path_check_modflow_step(util)
    if check_previous:
        return check_previous

    # TODO: check if Hydrus step was visited? (upload of projects is not mandatory)
    if util.get_hydrus_dir() is None or not util.loaded_project["hydrus_models"]:
        util.activate_error_flag()
        return redirect(endpoints.UPLOAD_HYDRUS)

    return None


def path_check_define_shapes_method(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to define_method.
    """

    check_previous = path_check_hydrus_step(util)
    if check_previous:
        return check_previous

    if util.current_method is None or util.loaded_shapes is None:
        # redirect to define method page if method was not selected
        util.activate_error_flag()
        return redirect(endpoints.DEFINE_METHOD)

    return None


# used in url_for(), requires base address of endpoint (for future)
def _format_endpoint_to_url(endpoint: str):
    return endpoint[1:].replace('-', '_')
