from typing import List

from kubernetes import client

from hydrus.hydrus_deployer_interface import IHydrusDeployer
from hydrus.kubernetes.hydrus_pod_deployer import _HydrusPodDeployer

# TODO: adapt to k8s cluster
HydrusDeployer = _HydrusPodDeployer


class HydrusMultiPodDeployer(IHydrusDeployer):

    # FIXME: here
    def __init__(self, api_instance: client.CoreV1Api, hydrus_projects_paths: List[str], pods_names: List[str],
                 namespace: str = ' default'):
        self.hydrus_instances = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_instances.append(HydrusDeployer(api_instance, path, pods_names[i], namespace=namespace))

    def run(self):
        deployed_pods = []
        for pod in self.hydrus_instances:
            deployed_pods.append(pod.run())
        return deployed_pods
