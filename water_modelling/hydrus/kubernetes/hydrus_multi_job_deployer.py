from __future__ import annotations
from typing import List

from hydrus.hydrus_deployer_interface import IHydrusDeployer
from hydrus.kubernetes.hydrus_job_deployer import _HydrusJobDeployer

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deployment.kubernetes_deployer import KubernetesDeployer


class HydrusMultiJobDeployer(IHydrusDeployer):

    def __init__(self, kubernetes_deployer: KubernetesDeployer, hydrus_projects_paths: List[str], job_names: List[str],
                 job_descriptions: List[str], namespace: str = 'default'):
        self.hydrus_instances = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_instances.append(
                _HydrusJobDeployer(kubernetes_deployer, path, job_names[i], job_descriptions[i], namespace=namespace))

    def run(self):
        for job in self.hydrus_instances:
            job.run()
        return self.hydrus_instances
