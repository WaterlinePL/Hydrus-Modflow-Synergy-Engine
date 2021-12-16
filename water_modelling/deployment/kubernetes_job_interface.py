from __future__ import annotations
from typing import Optional

from kubernetes.client import BatchV1Api, CoreV1Api, V1JobStatus

from hydrus.hydrus_deployer_interface import IHydrusDeployer
from modflow.modflow_deployer_interface import IModflowDeployer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployment.kubernetes_deployer import KubernetesDeployer


class IKubernetesJob(IModflowDeployer, IHydrusDeployer):

    def __init__(self, kubernetes_deployer: KubernetesDeployer, job_name: str,
                 sub_path: str, description: str, namespace: str = 'default'):
        self.kubernetes_deployer = kubernetes_deployer
        self.sub_path = sub_path
        self.job_name = job_name
        self.namespace = namespace
        self.description = description

    def run(self):
        """
        Run hydrological simulation as a Kubernetes job. This method is not supposed to be called, it indicates that
        a proper simulation deployer should implement it.
        @return: None
        """
        raise Exception("Unimplemented method!")

    def get_job_status(self) -> Optional[V1JobStatus]:
        """
        Return status of latest pod related to this job. Due to backoffLimit property, a failed job
        incarnates another pod to retry job. Access to status: job_status.status.[active|failed|succeded]
        @return: Latest pod status dict (None if job was not found by k8s).
        """
        job_status = self._get_k8s_batch_client().read_namespaced_job(name=self.job_name, namespace='default')
        if not job_status:
            return None
        return job_status.status

    def _get_k8s_batch_client(self) -> BatchV1Api:
        """
        Private method used to access k8s batch client (allows for creating jobs).
        @return: K8s batch client.
        """
        return self.kubernetes_deployer.batch_api_instance

    def _get_k8s_core_client(self) -> CoreV1Api:
        """
        Private method used to access k8s core client (allows for monitoring pods).
        @return: K8s core client.
        """
        return self.kubernetes_deployer.core_api_instance
