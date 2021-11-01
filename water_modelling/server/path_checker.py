from typing import Optional

from flask import Response, url_for, redirect

from server import endpoints
from server.app_utils import AppUtils


def path_check_modflow_step(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_modflow (first step).
    """

    if util.modflow_dir is None or not util.loaded_modflow_models:
        util.error_flag = True
        return redirect(url_for(endpoints.UPLOAD_MODFLOW))

    return None


def path_check_hydrus_step(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to upload_hydrus.
    """

    check_previous = path_check_modflow_step(util)
    if check_previous:
        return check_previous

    if util.hydrus_dir is None or not util.loaded_hydrus_models:
        util.error_flag = True
        return redirect(url_for(endpoints.UPLOAD_HYDRUS))

    return None


def path_check_define_shapes(util: AppUtils) -> Optional[Response]:
    """
    @param util: AppUtils containing current state of application.
    @return: Optional redirect to first incorrect step up to define_shapes.
    """

    check_previous = path_check_hydrus_step(util)
    if check_previous:
        return check_previous

    if not util.loaded_shapes:
        # redirect to define shapes page if shapes are not defined
        util.error_flag = True
        return redirect(url_for(endpoints.DEFINE_SHAPES, hydrus_model_index=0))

    return None
