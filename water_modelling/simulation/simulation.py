import os.path
from typing import Tuple

from datapassing.hydrus_modflow_passing import HydrusModflowPassing
from deployment.app_deployer_interface import IAppDeployer
from modflow import modflow_utils


class Simulation:
    def __init__(self, simulation_id: int, deployer: IAppDeployer):
        self.simulation_id = simulation_id
        self.deployer = deployer
        self.modflow_project = None
        self.loaded_shapes = None
        self.hydrus_finished = False
        self.passing_finished = False
        self.modflow_finished = False

    def run_simulation(self, modflow_dir: str, hydrus_dir: str):

        # ===== RUN HYDRUS INSTANCES ======
        self.run_hydrus(hydrus_dir)

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======
        nam_file = modflow_utils.get_nam_file(os.path.join(modflow_dir, self.modflow_project))
        self.pass_data_from_hydrus_to_modflow(hydrus_dir, modflow_dir, nam_file)

        # ===== RUN MODFLOW INSTANCE ======
        self.run_modflow(modflow_dir, nam_file)

    def run_modflow(self, modflow_dir: str, nam_file: str):
        assert self.modflow_project is not None
        modflow_project_dir = os.path.join(modflow_dir, self.modflow_project)

        self.deployer.run_modflow(modflow_project_dir, nam_file, self.simulation_id)
        self.modflow_finished = True
        print('Modflow container finished')

    def pass_data_from_hydrus_to_modflow(self, hydrus_dir, modflow_dir, nam_file: str):
        # Add hydrus result file paths (T_Level.out) to loaded_shapes (shape_file_info)
        for model_name_key in self.loaded_shapes:
            self.loaded_shapes[model_name_key].set_hydrus_recharge_output(
                os.path.join(hydrus_dir, model_name_key, "T_Level.out"))

        # Shapes list initialization from shape_file_info list
        print("Nam file", nam_file)
        shapes = HydrusModflowPassing.read_shapes_from_files(list(self.loaded_shapes.values()))
        result = HydrusModflowPassing(os.path.join(modflow_dir, self.modflow_project), nam_file, shapes)
        result.update_rch()

        self.passing_finished = True
        print("Passing successful")

    def run_hydrus(self, hydrus_dir: str):
        self.deployer.run_hydrus(hydrus_dir, self.loaded_shapes, self.simulation_id)
        self.hydrus_finished = True
        print('Hydrus containers finished')

    def set_modflow_project(self, modflow_project) -> None:
        self.modflow_project = modflow_project

    def set_loaded_shapes(self, loaded_shapes) -> None:
        self.loaded_shapes = loaded_shapes

    def get_simulation_status(self) -> Tuple[bool, bool, bool]:
        return self.hydrus_finished, self.passing_finished, self.modflow_finished

    def get_id(self) -> int:
        return self.simulation_id
