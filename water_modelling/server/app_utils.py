
import os

import numpy as np

import version_contants

from simulation.simulation_service import SimulationService
from datapassing.shape_data import ShapeFileData


def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


def get_or_none(req, key):
    return req.form[key] if req.form[key] != "" else None


class AppUtils:

    def __init__(self):
        self.allowed_types = ["ZIP", "RAR", "7Z"]
        self.project_root = version_contants.PROJECT_ROOT
        self.workspace_dir = os.path.join(self.project_root, 'workspace')
        self.loaded_project = None
        self.simulation_service = None
        self.current_method = None
        self.hydrus_exe = ""
        self.modflow_exe = ""
        self.recharge_masks = []
        self.models_masks_ids = {}
        self.loaded_shapes = {}
        self.error_flag = False

    def setup(self) -> None:
        self.current_method = None
        self.recharge_masks = []
        self.models_masks_ids = {}
        self.loaded_shapes = {}
        verify_dir_exists_or_create(self.workspace_dir)
        self.error_flag = False

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
        error_flag = self.error_flag
        self.error_flag = False
        return error_flag

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

    def init_simulation_service(self):
        if self.loaded_project is not None:
            self.simulation_service = SimulationService(self.get_hydrus_dir(), self.get_modflow_dir())

    def set_method(self, method):
        if self.current_method != method:
            self.models_masks_ids = {}
            self.loaded_shapes = {}
            self.current_method = method
        print("SET method", self.current_method)

    def get_current_model_by_id(self, rch_shape_index):
        current_model = None

        for hydrus_model in self.loaded_shapes:
            if self.models_masks_ids[hydrus_model] and rch_shape_index in self.models_masks_ids[hydrus_model]:
                current_model = hydrus_model

        return current_model

    def get_shapes_from_masks_ids(self):
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
                # TODO: better way to get shape of modflow model than np.shape(self.recharge_masks[0]))
                self.loaded_shapes[hydrus_model] = ShapeFileData(shape_mask_array=np.zeros(np.shape(self.recharge_masks[0])))