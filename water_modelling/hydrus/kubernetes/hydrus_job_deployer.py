from __future__ import annotations

import uuid

from kubernetes.client.rest import ApiException

from deployment.kubernetes_job_interface import IKubernetesJob
from utils.yaml_data import YamlData
from utils.yaml_job_generator import YamlJobGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployment.kubernetes_deployer import KubernetesDeployer


class _HydrusJobDeployer(IKubernetesJob):
    HYDRUS_VOLUME_MOUNT = "/workspace/hydrus"
    PROGRAMME_NAME = "Hydrus"
    CONTAINER_NAME = "hydrus1d-container"
    SHORTENED_UUID_LENGTH = 21

    def __init__(self, kubernetes_deployer: KubernetesDeployer, sub_path: str,
                 job_name: str, description: str , namespace: str = 'default'):
        super().__init__(kubernetes_deployer, job_name, sub_path, description, namespace)

    def run(self):
        resp = None
        try:
            resp = self._get_k8s_core_client().list_namespaced_pod(namespace="default",
                                                                   label_selector=f"job-name={self.job_name}")

        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)

        if resp.items:
            while resp.items:
                self.job_name = f"{self.sub_path.split('/hydrus/')[1]}-" \
                                f"{uuid.uuid4().hex[:_HydrusJobDeployer.SHORTENED_UUID_LENGTH]}"
                resp = self._get_k8s_core_client().list_namespaced_pod(namespace=self.namespace,
                                                                       label_selector=f"job-name={self.job_name}")
        yaml_data = YamlData(job_name=self.job_name,
                             container_image=self._get_hydrus_image(),
                             container_name=_HydrusJobDeployer.CONTAINER_NAME,
                             mount_path=_HydrusJobDeployer.HYDRUS_VOLUME_MOUNT,
                             args=[],
                             sub_path=self.sub_path,
                             hydro_program=_HydrusJobDeployer.PROGRAMME_NAME,
                             description=self.description)

        yaml_gen = YamlJobGenerator(yaml_data)
        job_manifest = yaml_gen.prepare_kubernetes_job()

        print("Job %s does not exist. Creating it..." % self.job_name)
        resp = self._get_k8s_batch_client().create_namespaced_job(body=job_manifest, namespace=self.namespace)

        return resp

    def get_model_name(self) -> str:
        return self.sub_path.split('/hydrus/')[1]

    def _get_hydrus_image(self):
        return self.kubernetes_deployer.hydrus_image
