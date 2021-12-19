from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from docker import APIClient
from docker.errors import APIError

from modflow import modflow_log_analyzer
from modflow.modflow_deployer_interface import IModflowDeployer
from simulation.simulation_error import SimulationError

if TYPE_CHECKING:
    from deployment.docker_deployer import DockerDeployer


class ModflowContainerDeployer(IModflowDeployer):
    MODFLOW_VOLUME_MOUNT = "/workspace"

    def __init__(self, docker_deployer: DockerDeployer, path: str, name_file: str, container_name: str = None):
        self.docker_deployer = docker_deployer
        self.path = path
        self.container_name = container_name
        self.name_file = name_file
        self.container_data = None

    def run(self):
        try:
            self.container_data = self._get_docker_client().inspect_container(self.container_name)
        except APIError as e:
            if e.status_code != 404:
                print(f"Error: {e}")
                exit(1)

        if not self.container_data:
            print("Container %s does not exist. Creating it..." % self.container_name)
            volume_mount_path = f"{self.path}:{ModflowContainerDeployer.MODFLOW_VOLUME_MOUNT}"
            host_config = self._get_docker_client().create_host_config(binds=[volume_mount_path])

            self.container_data = self._get_docker_client().create_container(image=self._get_modflow_image(),
                                                                             volumes=[self.path],
                                                                             host_config=host_config,
                                                                             name=self.container_name,
                                                                             command=[self._get_modflow_version(),
                                                                                      self.name_file])
            self._get_docker_client().start(self.container_data)

        return self.container_data

    def wait_for_termination(self) -> Optional[SimulationError]:
        self._get_docker_client().wait(self.container_data)

        # analyze output and return SimulationError if made
        # if log_lines with '\n' are needed: stream=True creates line generator (lines are bytes) - decode each
        # line with UTF-8 instead of splitting on '\n'
        log_lines = self._get_docker_client().logs(self.container_data, stream=False).decode("UTF-8").split('\n')
        simulation_error = modflow_log_analyzer.analyze_log(self._get_model_name(), log_lines)
        if simulation_error:
            print(f"{self.path}: error occurred: {simulation_error.error_description}")
            return simulation_error

        # successful scenario
        self._get_docker_client().remove_container(self.container_data)
        print(f"{self.container_name}: calculations completed successfully")
        return None

    def _get_modflow_version(self) -> str:
        return self.docker_deployer.modflow_version

    def _get_docker_client(self) -> APIClient:
        return self.docker_deployer.docker_client

    def _get_modflow_image(self) -> str:
        return self.docker_deployer.modflow_image

    def _get_model_name(self) -> str:
        return self.path.split('/modflow/')[1]
