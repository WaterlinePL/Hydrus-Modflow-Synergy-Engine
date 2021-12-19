import os.path
from typing import Tuple

from datapassing.hydrus_modflow_passing import HydrusModflowPassing
from deployment.app_deployer_interface import IAppDeployer
from modflow import modflow_utils
from simulation.exceptions import UnsuccessfulSimulationException
from simulation.simulation_stage_status import SimulationStageStatus


class Simulation:
    def __init__(self, simulation_id: int, deployer: IAppDeployer):
        self.simulation_id = simulation_id
        self.deployer = deployer
        self.spin_up = 0
        self.modflow_project = None
        self.loaded_shapes = None
        self.finished = False

        self._hydrus_stage_status = SimulationStageStatus()
        self._passing_stage_status = SimulationStageStatus()
        self._modflow_stage_status = SimulationStageStatus()

    def run_simulation(self, modflow_dir: str, hydrus_dir: str):

        # ===== RUN HYDRUS INSTANCES ======
        self.run_hydrus(hydrus_dir)

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======
        nam_file = modflow_utils.get_nam_file(os.path.join(modflow_dir, self.modflow_project))
        self.pass_data_from_hydrus_to_modflow(hydrus_dir, modflow_dir, nam_file)

        # ===== RUN MODFLOW INSTANCE ======
        self.run_modflow(modflow_dir, nam_file)
        self.set_finished_flag(modflow_dir)

    def run_modflow(self, modflow_dir: str, nam_file: str):
        assert self.modflow_project is not None
        modflow_project_dir = os.path.join(modflow_dir, self.modflow_project)
        simulation_error = self.deployer.run_modflow(modflow_project_dir, nam_file, self.simulation_id)

        if simulation_error:
            self._modflow_stage_status.add_error(simulation_error)
            self._modflow_stage_status.set_ended(True)
            raise UnsuccessfulSimulationException("Modflow simulation failed! Check 'simulation.log' file "
                                                  "inside model folder for full logs.")
        self._modflow_stage_status.set_ended(True)
        print('Modflow simulation finished')

    def pass_data_from_hydrus_to_modflow(self, hydrus_dir, modflow_dir, nam_file: str):
        # Add hydrus result file paths (T_Level.out) to loaded_shapes (shape_file_info)
        for model_name_key in self.loaded_shapes:
            self.loaded_shapes[model_name_key].set_hydrus_recharge_output(
                os.path.join(hydrus_dir, model_name_key, "T_Level.out"))

        # Shapes list initialization from shape_file_info list
        print("Nam file", nam_file)
        shapes = HydrusModflowPassing.read_shapes_from_files(list(self.loaded_shapes.values()))
        result = HydrusModflowPassing(os.path.join(modflow_dir, self.modflow_project), nam_file, shapes)
        result.update_rch(spin_up=self.spin_up)

        self._passing_stage_status.set_ended(True)
        print("Passing successful")

    def run_hydrus(self, hydrus_dir: str):
        simulation_errors = self.deployer.run_hydrus(hydrus_dir, self.loaded_shapes, self.simulation_id)
        contains_errors = False

        for error in simulation_errors:
            contains_errors = True
            self._hydrus_stage_status.add_error(error)

        if contains_errors:
            self._hydrus_stage_status.set_ended(True)
            raise UnsuccessfulSimulationException("Hydrus simulations failed! Check 'simulation.log' files "
                                                  "inside model folders for full logs.")
        self._hydrus_stage_status.set_ended(True)
        print('Hydrus simulations finished successfully')

    def set_modflow_project(self, modflow_project) -> None:
        self.modflow_project = modflow_project

    def set_loaded_shapes(self, loaded_shapes) -> None:
        self.loaded_shapes = loaded_shapes

    def set_spin_up(self, spin_up: int) -> None:
        self.spin_up = spin_up

    def get_hydrus_stage_status(self) -> SimulationStageStatus:
        return self._hydrus_stage_status

    def get_passing_stage_status(self) -> SimulationStageStatus:
        return self._passing_stage_status

    def get_modflow_stage_status(self) -> SimulationStageStatus:
        return self._modflow_stage_status

    def get_id(self) -> int:
        return self.simulation_id

    @staticmethod
    def set_finished_flag(modflow_dir: str) -> None:
        finished_file_path = os.path.join(modflow_dir, 'finished.0')
        finished_file = open(finished_file_path, "w")
        finished_file.close()
