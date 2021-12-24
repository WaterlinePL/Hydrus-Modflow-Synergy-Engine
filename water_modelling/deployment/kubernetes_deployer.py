import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import List

from kubernetes import config, client

from app_config import deployment_config
from deployment.app_deployer_interface import IAppDeployer

from hydrus.kubernetes.hydrus_multi_job_deployer import HydrusMultiJobDeployer
from kubernetes_controller.job_controller import JobController
from modflow.modflow_job_deployer import ModflowJobDeployer
from utils import path_formatter


class KubernetesDeployer(IAppDeployer):
    SHORTENED_UUID_LENGTH = 21

    MODFLOW_VERSIONS = ["mf2005"]
    MODFLOW_IMAGES = ["mjstealey/docker-modflow"]

    HYDRUS_IMAGES = ["watermodelling/hydrus-modflow-synergy-engine:hydrus1d_linux"]

    def __init__(self):
        self.hydrus_image = KubernetesDeployer.HYDRUS_IMAGES[0]
        self._set_modflow(0)

        if deployment_config.LOCAL_DEBUG_MODE:
            config.load_kube_config()
        else:
            config.load_incluster_config()

        self.core_api_instance = client.CoreV1Api()
        self.batch_api_instance = client.BatchV1Api()
        self.namespace = 'default'

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int):
        """
        Run all hydrus simulations in kubernetes cluster
        @param hydrus_dir: Directory containing projects inside main project
        @param hydrus_projects: Name of projects inside hydrus_dir
        @param sim_id: ID of the simulation
        @return: None
        """
        hydrus_count = len(hydrus_projects)
        hydrus_job_names = []
        hydrus_job_descriptions = []
        hydrus_volumes_sub_paths = []

        for project_name in hydrus_projects:
            hydrus_project_path = os.path.join(hydrus_dir, project_name)
            volume_sub_path = path_formatter.format_path_to_docker(dir_path=hydrus_project_path)
            volume_sub_path = path_formatter.extract_path_inside_workspace(volume_sub_path)[1:]
            hydrus_volumes_sub_paths.append(volume_sub_path)

            job_name = f"{volume_sub_path.split('/hydrus/')[1]}-" \
                       f"{uuid.uuid4().hex[:KubernetesDeployer.SHORTENED_UUID_LENGTH]}"
            job_description = f"Project={volume_sub_path.split('/hydrus/')[0]}, sim-id={str(sim_id)}"
            hydrus_job_names.append(job_name)
            hydrus_job_descriptions.append(job_description)

        multipod_deployer = HydrusMultiJobDeployer(kubernetes_deployer=self,
                                                   hydrus_projects_paths=hydrus_volumes_sub_paths,
                                                   job_names=hydrus_job_names,
                                                   namespace=self.namespace,
                                                   job_descriptions=hydrus_job_descriptions)

        deployed_jobs = multipod_deployer.run()  # run all hydrus jobs inside pods
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(JobController.wait_for_pod_termination, deployed_jobs)

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id):
        """
        Run modflow simulation in kubernetes cluster
        @param modflow_dir: Directory containing modflow project (inside main project)
        @param nam_file: Name of .nam file inside the Modflow project
        @param sim_id: ID of the simulation
        @return: None
        """
        volume_sub_path = path_formatter.format_path_to_docker(dir_path=modflow_dir)
        volume_sub_path = path_formatter.extract_path_inside_workspace(volume_sub_path)[1:]

        modflow_job_name = f"{volume_sub_path.split('/modflow/')[1]}-" \
                           f"{uuid.uuid4().hex[:KubernetesDeployer.SHORTENED_UUID_LENGTH]}"
        modflow_job_description = f"Project={volume_sub_path.split('/modflow/')[0]}, sim-id={str(sim_id)}"
        modflow_deployer = ModflowJobDeployer(kubernetes_deployer=self, sub_path=volume_sub_path,
                                              name_file=nam_file, job_name=modflow_job_name,
                                              namespace=self.namespace, description=modflow_job_description)
        modflow_deployer.run()  # run modflow job inside pod
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(JobController.wait_for_pod_termination, modflow_deployer)

    def _set_modflow(self, i: int):
        self.modflow_version = KubernetesDeployer.MODFLOW_VERSIONS[i]
        self.modflow_image = KubernetesDeployer.MODFLOW_IMAGES[i]


def create() -> KubernetesDeployer:
    return KubernetesDeployer()
