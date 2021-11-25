import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from modflow.modflow_desktop_deployer import ModflowDesktopDeployer
from deployment.app_deployer_interface import IAppDeployer

from hydrus.desktop.hydrus_multi_deployer import HydrusLocalMultiDeployer

import server.local_configuration_dao as lcd


class DesktopDeployer(IAppDeployer):

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int):
        """
        Run all hydrus simulations in system shell processes
        @param hydrus_dir: Directory containing projects inside main project
        @param hydrus_projects: Name of projects inside hydrus_dir
        @param sim_id: ID of the simulation
        @return: None
        """
        hydrus_count = len(hydrus_projects)
        hydrus_volumes_paths = []
        for project_name in hydrus_projects:
            hydrus_project_path = os.path.join(hydrus_dir, project_name)
            hydrus_volumes_paths.append(hydrus_project_path)

        hydrus_exe_path = lcd.read_configuration()["hydrus_exe"]
        multi_deployer = HydrusLocalMultiDeployer(hydrus_exe_path, hydrus_volumes_paths)

        multi_deployer.run()    # run all hydrus instances
        hydrus_instances = multi_deployer.get_hydrus_instances()
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            for instance in hydrus_instances:
                exe.submit(instance.wait_for_termination)

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id):
        """
        Run modflow simulation in system shell process
        @param modflow_dir: Directory containing modflow project (inside main project)
        @param nam_file: Name of .nam file inside the Modflow project
        @param sim_id: ID of the simulation
        @return: None
        """
        modflow_exe_path = lcd.read_configuration()["modflow_exe"]
        modflow_deployer = ModflowDesktopDeployer(modflow_exe_path, modflow_dir, nam_file)
        modflow_deployer.run()  # run modflow pod
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(modflow_deployer.wait_for_termination)


def create() -> DesktopDeployer:
    return DesktopDeployer()
