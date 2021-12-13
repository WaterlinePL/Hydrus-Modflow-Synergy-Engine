from __future__ import annotations
from kubernetes.client.rest import ApiException

from deployment.kubernetes_job_interface import IKubernetesJob
from utils.yaml_data import YamlData
from utils.yaml_generator import YamlGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployment.kubernetes_deployer import KubernetesDeployer


class ModflowJobDeployer(IKubernetesJob):
    MODFLOW_VOLUME_MOUNT = '/workspace'

    def __init__(self, kubernetes_deployer: KubernetesDeployer, sub_path: str, name_file: str, job_name: str,
                 namespace: str = 'default'):
        super().__init__(kubernetes_deployer, job_name, sub_path, namespace)
        self.name_file = name_file

    def run(self):
        resp = None
        try:
            resp = self._get_k8s_core_client().list_namespaced_pod(namespace='default',
                                                                   label_selector=f'job-name={self.job_name}')

        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)

        if not resp.items:
            yaml_data = YamlData(job_name=self.job_name,
                                 container_image=self._get_modflow_image(),
                                 container_name='modflow-container',
                                 mount_path=ModflowJobDeployer.MODFLOW_VOLUME_MOUNT,
                                 args=[self._get_modflow_version(),
                                       self.name_file],
                                 sub_path=self.sub_path)

            yaml_gen = YamlGenerator(yaml_data)
            job_manifest = yaml_gen.prepare_kubernetes_job()

            print("Job %s does not exist. Creating it..." % self.job_name)
            resp = self._get_k8s_batch_client().create_namespaced_job(body=job_manifest, namespace=self.namespace)
        else:
            print(f"Job {self.job_name} already exists in cluster!")

        return resp

    def _get_modflow_image(self):
        return self.kubernetes_deployer.modflow_image
        # return "observer46/water_modeling_agh:hydrus1d_linux"

    def _get_modflow_version(self):
        return self.kubernetes_deployer.modflow_version
