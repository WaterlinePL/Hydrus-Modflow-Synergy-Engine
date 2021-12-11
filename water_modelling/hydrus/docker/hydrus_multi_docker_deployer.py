from __future__ import annotations
from typing import List, TYPE_CHECKING

from hydrus.docker.hydrus_docker_deployer import HydrusDockerContainerDeployer
from hydrus.hydrus_deployer_interface import IHydrusDeployer

if TYPE_CHECKING:
    from deployment.docker_deployer import DockerDeployer


class HydrusDockerMultiContainerDeployer(IHydrusDeployer):

    def __init__(self, docker_deployer: DockerDeployer, hydrus_projects_paths: List[str], container_names: List[str]):
        self.hydrus_instances = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_instances.append(HydrusDockerContainerDeployer(docker_deployer, path, container_names[i]))

    def run(self):
        for container in self.hydrus_instances:
            container.run()

    def get_hydrus_containers(self) -> List[HydrusDockerContainerDeployer]:
        return self.hydrus_instances
