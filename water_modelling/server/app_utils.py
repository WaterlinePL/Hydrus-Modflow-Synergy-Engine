
import os

import version_contants

from simulation.simulation_service import SimulationService


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
        self.recharge_masks = []
        self.loaded_shapes = {}
        self.error_flag = False

    def setup(self) -> None:
        self.recharge_masks = []
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
