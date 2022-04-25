from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import os

import numpy as np
from app_config import deployment_config
from datapassing.shape_data import ShapeMetadata
from simulation.exceptions import NoLoadedProjectException

if TYPE_CHECKING:
    from simulation.simulation_service import SimulationService


def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


def get_or_none(req, key):
    return req.form[key] if req.form[key] != "" else None


class UserState:

    def __init__(self):
        self.loaded_project = None
        self.simulation_service: Optional[SimulationService] = None
        self.current_method = None
        self.recharge_masks = []
        self.models_masks_ids = {}
        self.loaded_shapes = {}
        self._error_flag = False

    @staticmethod
    def get_modflow_dir_by_project_name(project_name):
        if project_name is not None:
            return os.path.join(deployment_config.WORKSPACE_DIR, project_name, 'modflow')
        else:
            return None

    @staticmethod
    def type_allowed(filename: str) -> bool:
        """
        @param filename: Path to the file whose extension needs to be checked
        @return: True if file has valid extension, False otherwise
        """

        # check if there even is an extension
        if '.' not in filename:
            return False

        # check if it's allowed
        extension = filename.rsplit('.', 1)[1]
        return extension.upper() in deployment_config.ALLOWED_UPLOAD_TYPES

    def setup(self) -> None:
        self.reset_project_data()
        verify_dir_exists_or_create(deployment_config.WORKSPACE_DIR)

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
            return os.path.join(deployment_config.WORKSPACE_DIR, self.loaded_project['name'], 'modflow')
        else:
            return None

    def get_hydrus_dir(self):
        if self.loaded_project is not None:
            return os.path.join(deployment_config.WORKSPACE_DIR, self.loaded_project['name'], 'hydrus')
        else:
            return None

    def get_error_flag(self) -> bool:
        error_flag = self._error_flag
        self._error_flag = False
        return error_flag

    def activate_error_flag(self):
        self._error_flag = True

    def set_simulation_service(self, simulation_service: SimulationService):
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
                shape_mask = self.recharge_masks[self.models_masks_ids[hydrus_model][0]]

            elif shapes_count > 1:
                shape_mask = self.recharge_masks[self.models_masks_ids[hydrus_model][0]]
                for idx in range(1, shapes_count):
                    another_mask = self.recharge_masks[self.models_masks_ids[hydrus_model][idx]]
                    shape_mask = np.logical_or(shape_mask, another_mask)

            else:
                shape_mask = self.create_empty_mask()

            shape_metadata = ShapeMetadata(shape_mask_array=shape_mask,
                                           main_project_name=self.loaded_project["name"],
                                           hydrus_model_name=hydrus_model)
            self.loaded_shapes[hydrus_model] = shape_metadata
            shape_metadata.dump_to_file()

    # TODO: Probably move elsewhere
    def create_empty_mask(self) -> Optional[np.ndarray]:
        """
        Creates an empty shape mask as an NumPy array

        @return: a ShapeFileData instance with an empty mask the size of the currently loaded model,
            or None if no project is loaded
        """
        if not self.loaded_project:
            raise NoLoadedProjectException("Tried to create empty mask without loading a project!")
        else:
            return np.zeros((self.loaded_project["rows"], self.loaded_project["cols"]))
