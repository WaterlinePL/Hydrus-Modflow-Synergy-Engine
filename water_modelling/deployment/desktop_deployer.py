import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from modflow.modflow_desktop_deployer import ModflowDesktopDeployer
from deployment.app_deployer_interface import IAppDeployer

from hydrus.desktop.hydrus_multi_deployer import HydrusLocalMultiDeployer

import server.local_configuration_dao as lcd
from simulation.simulation_error import SimulationError


class DesktopDeployer(IAppDeployer):

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int) -> List[SimulationError]:
        """
        Run all hydrus simulations in system shell processes
        @param hydrus_dir: Directory containing projects inside main project
        @param hydrus_projects: Name of projects inside hydrus_dir
        @param sim_id: ID of the simulation
        @return: List of errors that occurred during Hydrus simulations (one per simulation)
        """
        hydrus_count = len(hydrus_projects)
        hydrus_volumes_paths = []
        for project_name in hydrus_projects:
            hydrus_project_path = os.path.join(hydrus_dir, project_name)
            hydrus_volumes_paths.append(hydrus_project_path)

        hydrus_exe_path = lcd.read_configuration()["hydrus_exe"]
        multi_deployer = HydrusLocalMultiDeployer(hydrus_exe_path, hydrus_volumes_paths)

        multi_deployer.run()  # run all hydrus instances
        hydrus_instances = multi_deployer.get_hydrus_instances()
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            potential_simulation_errors = []
            for instance in hydrus_instances:
                potential_simulation_errors.append(exe.submit(instance.wait_for_termination))

            simulation_errors = []
            for future in potential_simulation_errors:
                error = future.result()
                if error:
                    simulation_errors.append(error)
            return simulation_errors

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id) -> Optional[SimulationError]:
        """
        Run modflow simulation in system shell process
        @param modflow_dir: Directory containing modflow project (inside main project)
        @param nam_file: Name of .nam file inside the Modflow project
        @param sim_id: ID of the simulation
        @return: Optionally an error that occurred during Modflow simulation
        """
        modflow_exe_path = lcd.read_configuration()["modflow_exe"]
        modflow_deployer = ModflowDesktopDeployer(modflow_exe_path, modflow_dir, nam_file)
        modflow_deployer.run()  # run modflow simulation
        with ThreadPoolExecutor(max_workers=1) as exe:
            error_future = exe.submit(modflow_deployer.wait_for_termination)
            error = error_future.result()
            if error:
                return error
        return None


def create() -> DesktopDeployer:
    return DesktopDeployer()
