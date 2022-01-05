import os
import subprocess
from typing import Optional

from modflow import modflow_log_analyzer
from modflow.modflow_deployer_interface import IModflowDeployer
from simulation.simulation_error import SimulationError
from utils import path_formatter


class ModflowDesktopDeployer(IModflowDeployer):

    LOG_FILE = "simulation.log"

    def __init__(self, modflow_exe_path: str, path: str, name_file: str):
        self.modflow_exe_path = path_formatter.convert_backslashes_to_slashes(modflow_exe_path)
        self.path = path
        self.name_file = name_file
        self.proc = None

    def run(self):
        current_dir = os.getcwd()
        os.chdir(self.path)
        print(f"Starting Modflow calculations for: {path_formatter.convert_backslashes_to_slashes(self.path)}")

        with open(self._get_path_to_log(), 'w') as handle:
            self.proc = subprocess.Popen([self.modflow_exe_path, self.name_file], shell=True, text=True,
                                         stdin=subprocess.PIPE, stdout=handle, stderr=handle)
        os.chdir(current_dir)

    def wait_for_termination(self) -> Optional[SimulationError]:
        self.proc.communicate(input="\n")

        # analyze output and return SimulationError if made
        with open(self._get_path_to_log(), 'r') as handle:
            log_lines = handle.readlines()
            simulation_error = modflow_log_analyzer.analyze_log(self._get_model_name(), log_lines)
            if simulation_error:
                print(f"{self.path}: error occurred: {simulation_error.error_description}")
                return simulation_error

        # successful scenario
        print(f"{self.name_file}: calculations completed successfully")
        return None

    def _get_model_name(self) -> str:
        return path_formatter.convert_backslashes_to_slashes(self.path).split('/modflow/')[1]

    def _get_path_to_log(self) -> str:
        return os.path.join(self.path, ModflowDesktopDeployer.LOG_FILE)
