from typing import List

from hydrus.desktop.hydrus_desktop_deployer import _HydrusDesktopDeployer
from hydrus.hydrus_deployer_interface import IHydrusDeployer


class HydrusLocalMultiDeployer(IHydrusDeployer):

    def __init__(self, hydrus_exe_path: str, hydrus_projects_paths: List[str]):
        self.hydrus_instances = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_instances.append(_HydrusDesktopDeployer(hydrus_exe_path, path))

    def run(self):
        for instance in self.hydrus_instances:
            instance.run()

    def get_hydrus_instances(self):
        return self.hydrus_instances
