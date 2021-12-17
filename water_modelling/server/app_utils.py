from __future__ import annotations

from sys import platform
from typing import TYPE_CHECKING

import os

import numpy as np

from server.endpoints import RCH_SHAPES

from datapassing.shape_data import ShapeFileData

if TYPE_CHECKING:
    from simulation.simulation_service import SimulationService

if platform == "linux" or platform == "linux2" or platform == "darwin":
    PROJECT_ROOT = "../"
elif platform == "win32":
    PROJECT_ROOT = "..\\"


def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


def get_or_none(req, key):
    return req.form[key] if req.form[key] != "" else None


def fix_model_name(name: str):
    """
    Takes a filename string and makes it safe for further use. This method will probably need expanding.
    E.g. "modflow .1.zip" becomes "modflow__1.zip". Also file names will be truncated to 40 characters.

    @param name: the name of the file uploaded by the user
    @return: that name, made safe for the app to use
    """
    dots = name.count('.') - 1  # for when someone decides to put a dot in the filename
    name = name.replace(" ", "-").replace(".", "-", dots)  # remove whitespace and extra dots
    if len(name) > 44:  # truncate name to 40 characters long (+4 for ".zip")
        split = name.split('.')
        split[0] = split[0][0:40]
        name = ".".join(split)
    return name


# Ta klasa stała się reactowym state XD
class AppUtils:

    def __init__(self):
        self.allowed_types = ["ZIP"]
        self.project_root = os.path.abspath(PROJECT_ROOT)
        self.workspace_dir = os.path.join(self.project_root, 'workspace')
        self.loaded_project = None
        self.simulation_service = None
        self.current_method = None
        self.recharge_masks = []
        self.models_masks_ids = {}
        self.loaded_shapes = {}
        self._error_flag = False

    def setup(self) -> None:
        self.reset_project_data()
        verify_dir_exists_or_create(self.workspace_dir)

    def reset_project_data(self) -> None:
        self.loaded_project = None
        self.simulation_service = None
        self.current_method = None
        self.recharge_masks = []
        self.models_masks_ids = {}
        self.loaded_shapes = {}
        self._error_flag = False

    def get_modflow_dir(self):
        if self.loaded_project is not None:
            return os.path.join(self.workspace_dir, self.loaded_project['name'], 'modflow')
        else:
            return None

    def get_hydrus_dir(self):
        if self.loaded_project is not None:
            return os.path.join(self.workspace_dir, self.loaded_project['name'], 'hydrus')
        else:
            return None

    def get_error_flag(self) -> bool:
        error_flag = self._error_flag
        self._error_flag = False
        return error_flag

    def activate_error_flag(self):
        self._error_flag = True

    def type_allowed(self, filename: str) -> bool:
        """
        @param filename: Path to the file whose extension needs to be checked
        @return: True if file has valid extension, False otherwise
        """

        # check if there even is an extension
        if '.' not in filename:
            return False

        # check if it's allowed
        extension = filename.rsplit('.', 1)[1]
        return extension.upper() in self.allowed_types

    def set_simulation_serivce(self, simulation_service: SimulationService):
        self.simulation_service = simulation_service

    def set_method(self, method):
        if self.current_method != method:
            self.models_masks_ids = {}
            self.loaded_shapes = {}
            self.current_method = method

    def get_current_model_by_id(self, rch_shape_index):
        current_model = None

        for hydrus_model in self.loaded_shapes:
            if self.models_masks_ids[hydrus_model] and rch_shape_index in self.models_masks_ids[hydrus_model]:
                current_model = hydrus_model

        return current_model

    def get_shapes_from_masks_ids(self):
        """
        models_masks_ids dictionary contains hydrus models names as a key and array of indexes as values.
        Array stores indexes of shapes in the recharge_mask array.
        This method for each hydrus model evaluates array of indexes to the shape mask and creates
        ShapeFileData object.
        :return: None
        """

        for hydrus_model in self.loaded_shapes:
            shapes_count = -1
            if self.models_masks_ids[hydrus_model]:
                shapes_count = len(self.models_masks_ids[hydrus_model])

            if shapes_count == 1:
                self.loaded_shapes[hydrus_model] = ShapeFileData(shape_mask_array=
                                                                 self.recharge_masks[self.models_masks_ids[hydrus_model][0]])
            elif shapes_count > 1:
                shape_mask = self.recharge_masks[self.models_masks_ids[hydrus_model][0]]
                for idx in range(1, shapes_count):
                    shape_mask = np.logical_or(shape_mask, self.recharge_masks[self.models_masks_ids[hydrus_model][idx]])

                self.loaded_shapes[hydrus_model] = ShapeFileData(shape_mask_array=shape_mask)
            else:
                shape = (self.loaded_project["rows"], self.loaded_project["cols"])
                self.loaded_shapes[hydrus_model] = ShapeFileData(shape_mask_array=np.zeros(shape))


# Initiate singleton setup
util = AppUtils()
util.setup()
