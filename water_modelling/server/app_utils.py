
import os

import version_contants

from simulation.simulation_service import SimulationService


def verify_dir_exists_or_create(path: str):
    if not os.path.isdir(path):
        print('Directory ' + path + ' does not exist, creating...')
        os.system('mkdir ' + path)


class AppUtils:

    def __init__(self):
        self.allowed_types = ["ZIP", "RAR", "7Z"]
        self.project_root = version_contants.PROJECT_ROOT
        self.workspace_dir = os.path.join(self.project_root, 'workspace')
        self.loaded_project = None
        self.loaded_hydrus_models = []  # an array of strings, the names of the loaded hydrus models
        self.loaded_modflow_models = []
        self.simulation_service = None
        self.nam_file_name = ""
        self.recharge_masks = []
        self.loaded_shapes = {}
        self.modflow_rows = 0
        self.modflow_cols = 0
        self.error_flag = False

    def setup(self) -> None:
        self.loaded_hydrus_models = []
        self.loaded_modflow_models = []
        self.nam_file_name = ""
        self.recharge_masks = []
        self.loaded_shapes = {}
        self.modflow_rows = 0
        self.modflow_cols = 0
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
