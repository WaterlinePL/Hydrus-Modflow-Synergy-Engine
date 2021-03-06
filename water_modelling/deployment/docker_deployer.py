import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

import docker

from deployment.app_deployer_interface import IAppDeployer
from hydrus.docker.hydrus_multi_docker_deployer import HydrusDockerMultiContainerDeployer
from modflow.modflow_docker_deployer import ModflowContainerDeployer
from simulation.simulation_error import SimulationError
from utils import path_formatter


class DockerDeployer(IAppDeployer):
    MODFLOW_VERSIONS = ["mf2005"]
    MODFLOW_IMAGES = ["mjstealey/docker-modflow"]

    HYDRUS_IMAGES = ["watermodelling/hydrus-modflow-synergy-engine:hydrus1d_linux"]

    def __init__(self):
        self.docker_client = docker.APIClient()

        # Works, provided we maintain the order of volumes inside docker-compose.yml -> ['Mounts'][0]['Source']
        # as workspace volume is first on the list
        self.workspace_volume = DockerDeployer._get_workspace_mount(
            self.docker_client.inspect_container(
                os.environ["HOSTNAME"])['Mounts'])

        print(f"Workspace original path: {self.workspace_volume}")

        self.hydrus_image = DockerDeployer.HYDRUS_IMAGES[0]
        self._set_modflow(0)

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int) -> List[SimulationError]:
        project_name = path_formatter.extract_project_name(hydrus_dir)
        hydrus_volumes_paths = []
        hydrus_container_names = []

        for hydrus_model_name in hydrus_projects:
            hydrus_container_names.append(f"{sim_id}-{project_name}-hydrus-{hydrus_model_name}-{uuid.uuid4().hex}")

            workspace_project_path = path_formatter.extract_path_inside_workspace(
                os.path.join(hydrus_dir, hydrus_model_name))

            hydrus_volumes_paths.append(path_formatter.format_path_to_docker(dir_path=self.workspace_volume)
                                        + workspace_project_path)

        multi_container_deployer = HydrusDockerMultiContainerDeployer(docker_deployer=self,
                                                                      hydrus_projects_paths=hydrus_volumes_paths,
                                                                      container_names=hydrus_container_names)
        hydrus_containers = multi_container_deployer.run()  # run all hydrus containers

        with ThreadPoolExecutor(max_workers=len(hydrus_containers)) as exe:
            potential_simulation_errors = []
            for container in hydrus_containers:
                potential_simulation_errors.append(exe.submit(container.wait_for_termination))

            simulation_errors = []
            for future in potential_simulation_errors:
                error = future.result()
                if error:
                    simulation_errors.append(error)
            return simulation_errors

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id) -> Optional[SimulationError]:
        project_name = path_formatter.extract_project_name(modflow_dir)
        modflow_model_name = path_formatter.extract_hydrological_model_name(modflow_dir)
        modflow_container_name = f"{sim_id}-{project_name}-modflow-{modflow_model_name}-{uuid.uuid4().hex}"
        workspace_project_path = path_formatter.extract_path_inside_workspace(modflow_dir)

        modflow_volume_path = path_formatter.format_path_to_docker(dir_path=self.workspace_volume) \
                              + workspace_project_path

        modflow_deployer = ModflowContainerDeployer(docker_deployer=self, path=modflow_volume_path,
                                                    name_file=nam_file, container_name=modflow_container_name)
        modflow_deployer.run()  # run modflow container
        with ThreadPoolExecutor(max_workers=1) as exe:
            error_future = exe.submit(modflow_deployer.wait_for_termination)
            error = error_future.result()
            if error:
                return error
        return None

    def _set_modflow(self, i: int):
        self.modflow_version = DockerDeployer.MODFLOW_VERSIONS[i]
        self.modflow_image = DockerDeployer.MODFLOW_IMAGES[i]

    @staticmethod
    def _get_workspace_mount(mounts):
        socket_path = "/var/run/docker.sock"
        for mount in mounts:
            if socket_path not in mount['Source']:
                return mount['Source']


def create() -> DockerDeployer:
    return DockerDeployer()
