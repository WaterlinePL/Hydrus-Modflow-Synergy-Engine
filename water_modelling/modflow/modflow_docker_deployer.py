from __future__ import annotations
from typing import TYPE_CHECKING
from time import sleep

from docker import APIClient
from docker.errors import APIError

from modflow.modflow_deployer_interface import IModflowDeployer

if TYPE_CHECKING:
    from deployment.docker_deployer import DockerDeployer


class ModflowContainerDeployer(IModflowDeployer):

    def __init__(self, docker_deployer: DockerDeployer, path: str, name_file: str, container_name: str = None):
        self.docker_deployer = docker_deployer
        self.path = path
        self.container_name = container_name
        self.name_file = name_file

    def run(self):
        container = None
        try:
            container = self._get_docker_client().inspect_container(self.container_name)
        except APIError as e:
            if e.status_code != 404:
                print(f"Error: {e}")
                exit(1)

        if not container:
            print("Container %s does not exist. Creating it..." % self.container_name)
            host_config = self._get_docker_client().create_host_config(auto_remove=True,
                                                                       binds=[f"{self.path}:/workspace"])

            container = self._get_docker_client().create_container(image=self._get_modflow_image(),
                                                                   volumes=[self.path],
                                                                   host_config=host_config,
                                                                   name=self.container_name,
                                                                   command=[self._get_modflow_version(),
                                                                            self.name_file])
            self._get_docker_client().start(container)

        return container

    def wait_for_termination(self):
        while not self._is_completed():
            sleep(2)
        print(f"{self.container_name} completed calculations")

    def _is_completed(self) -> bool:
        try:
            container_status = self._get_docker_client().inspect_container(self.container_name)['State']
            if container_status['ExitCode'] != 0:
                print(f"Error on container: {self.container_name}")
            return not container_status['Running']
        except APIError as e:
            if e.status_code != 404:
                print(f"Error: {e}")
                exit(1)
            return True

    def _get_modflow_version(self) -> str:
        return self.docker_deployer.modflow_version

    def _get_docker_client(self) -> APIClient:
        return self.docker_deployer.docker_client

    def _get_modflow_image(self) -> str:
        return self.docker_deployer.modflow_image
