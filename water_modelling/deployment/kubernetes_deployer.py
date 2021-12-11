import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

from kubernetes import config, client

from deployment.app_deployer_interface import IAppDeployer

from hydrus.desktop.hydrus_multi_deployer import HydrusLocalMultiDeployer
from kubernetes_controller.pod_controller import PodController
from modflow.modflow_pod_deployer import ModflowPodDeployer
from utils import path_formatter as PathFormatter


# TODO: adapt to kubernetes cluster
class KubernetesDeployer(IAppDeployer):

    def __init__(self, modflow_image: str = "observer46/water_modeling_agh:hydrus1d_linux",
                 hydrus_image: str = "mjstealey/docker-modflow"):

        self.modflow_image = modflow_image
        self.hydrus_image = hydrus_image

        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.pod_controller = PodController(self.api_instance)
        self.namespace = "water_modelling"

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int):
        """
        Run all hydrus simulations in kubernetes cluster
        @param hydrus_dir: Directory containing projects inside main project
        @param hydrus_projects: Name of projects inside hydrus_dir
        @param sim_id: ID of the simulation
        @return: None
        """
        hydrus_count = len(hydrus_projects)
        hydrus_pod_names = ["hydrus-pod-id." + str(sim_id) + "-num." + str(i + 1) for i in
                            range(hydrus_count)]

        hydrus_volumes_paths = []
        for project_name in hydrus_projects:
            hydrus_project_path = os.path.join(hydrus_dir, project_name)
            hydrus_volumes_paths.append(PathFormatter.format_path_to_docker(dir_path=hydrus_project_path))
        multipod_deployer = HydrusLocalMultiDeployer(api_instance=self.api_instance,
                                                     hydrus_projects_paths=hydrus_volumes_paths,
                                                     pods_names=hydrus_pod_names,
                                                     namespace=self.namespace)

        multipod_deployer.run()  # run all hydrus pods
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(self.pod_controller.wait_for_pod_termination, hydrus_pod_names)

    # FIXME: write in docstring: modflow_dir is project dir
    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id):
        """
        Run modflow simulation in kubernetes cluster
        @param modflow_dir: Directory containing modflow project (inside main project)
        @param nam_file: Name of .nam file inside the Modflow project
        @param sim_id: ID of the simulation
        @return: None
        """
        modflow_pod_name = "modflow-2005-id." + str(sim_id)
        modflow_volume_path = PathFormatter.format_path_to_docker(dir_path=modflow_dir)
        modflow_deployer = ModflowPodDeployer(api_instance=self.api_instance, path=modflow_volume_path,
                                              name_file=nam_file, pod_name=modflow_pod_name, namespace=self.namespace)
        modflow_v1_pod = modflow_deployer.run()  # run modflow pod
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(self.pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)


deployer = KubernetesDeployer()
