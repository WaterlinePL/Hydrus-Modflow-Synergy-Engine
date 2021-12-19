import os
import subprocess
from typing import Optional

from hydrus import hydrus_log_analyzer
from hydrus.hydrus_deployer_interface import IHydrusDeployer
from simulation.simulation_error import SimulationError
from utils import path_formatter


class _HydrusDesktopDeployer(IHydrusDeployer):
    LOG_FILE = "simulation.log"

    def __init__(self, hydrus_exe_path: str, path: str):
        self.hydrus_exe_path = path_formatter.convert_backslashes_to_slashes(hydrus_exe_path)
        self.path = path_formatter.convert_backslashes_to_slashes(path)
        self.proc = None

    def run(self):
        print(f"Starting Hydrus calculations for: {self.path}")
        with open(self._get_path_to_log(), 'w') as handle:
            self.proc = subprocess.Popen([self.hydrus_exe_path, self.path], shell=True, text=True,
                                         stdin=subprocess.PIPE, stdout=handle, stderr=handle)

    def wait_for_termination(self) -> Optional[SimulationError]:
        self.proc.communicate(input="\n")  # Press that stupid enter (blocking)

        # analyze output and return SimulationError if made
        with open(self._get_path_to_log(), 'r') as handle:
            log_lines = handle.readlines()
            simulation_error = hydrus_log_analyzer.analyze_log(self._get_model_name(), log_lines)
            if simulation_error:
                print(f"{self.path}: error occurred: {simulation_error.error_description}")
                return simulation_error

        # successful scenario
        print(f"{self.path}: calculations completed successfully")
        return None

    def _get_model_name(self) -> str:
        return path_formatter.convert_backslashes_to_slashes(self.path).split('/hydrus/')[1]

    def _get_path_to_log(self) -> str:
        return os.path.join(self.path, _HydrusDesktopDeployer.LOG_FILE)
