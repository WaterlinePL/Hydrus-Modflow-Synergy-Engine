import subprocess

from hydrus.hydrus_deployer_interface import IHydrusDeployer
from utils import path_formatter

import app_config.deployment_config as deployment_config


class _HydrusDesktopDeployer(IHydrusDeployer):

    def __init__(self, hydrus_exe_path: str, path: str):
        self.hydrus_exe_path = path_formatter.convert_backslashes_to_slashes(hydrus_exe_path)
        self.path = path_formatter.convert_backslashes_to_slashes(path)
        self.proc = None

    def run(self):
        stdout = subprocess.DEVNULL if not deployment_config.LOCAL_DEBUG_MODE else None
        print(f"Starting Hydrus calculations for: {self.path}")
        self.proc = subprocess.Popen([self.hydrus_exe_path, self.path], shell=True, text=True,
                                     stdin=subprocess.PIPE, stdout=stdout)

    def wait_for_termination(self):
        self.proc.communicate(input="\n")  # Press that stupid enter (blocking)
        print(f"{self.path} completed calculations")
