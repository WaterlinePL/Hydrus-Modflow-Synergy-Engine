import os
import subprocess

from app_config import deployment_config
from modflow.modflow_deployer_interface import IModflowDeployer
from utils import path_formatter


class ModflowDesktopDeployer(IModflowDeployer):

    def __init__(self, modflow_exe_path: str, path: str, name_file: str):
        self.modflow_exe_path = path_formatter.convert_backslashes_to_slashes(modflow_exe_path)
        self.path = path
        self.name_file = name_file
        self.proc = None

    def run(self):
        # schema for future testing:
        # if platform == "linux" or platform == "linux2":
        #     pass
        # elif platform == "darwin":  # OS X(D)
        #     pass
        # elif platform == "win32":
        self.run_for_win_10()

    def run_for_win_10(self):
        current_dir = os.getcwd()
        os.chdir(self.path)
        stdout = subprocess.DEVNULL if not deployment_config.DEBUG_MODE else None
        print(f"Starting Modflow calculations for: {path_formatter.convert_backslashes_to_slashes(self.path)}")
        self.proc = subprocess.Popen([self.modflow_exe_path, self.name_file], shell=True, text=True,
                                     stdin=subprocess.PIPE, stdout=stdout)
        os.chdir(current_dir)

    def wait_for_termination(self):
        self.proc.communicate(input="\n")  # Press that stupid enter (blocking)
        print(f"{self.name_file} completed calculations")
