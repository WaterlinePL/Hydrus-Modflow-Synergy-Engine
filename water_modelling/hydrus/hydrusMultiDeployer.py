from typing import List

from kubernetes import client

from hydrus.IHydrusDeployer import IHydrusDeployer
from hydrus.hydrusPodDeployer import HydrusPodDeployer

# TODO: switcharoo (get rid of kubernetes pods)
HydrusDeployer = HydrusPodDeployer


class HydrusMultiDeployer(IHydrusDeployer):

    def __init__(self, api_instance: client.CoreV1Api, hydrus_projects_paths: List[str], pods_names: List[str],
                 namespace: str = ' default'):
        self.hydrus_pods = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_pods.append(HydrusDeployer(api_instance, path, pods_names[i], namespace=namespace))

    def run(self):
        deployed_pods = []
        for pod in self.hydrus_pods:
            deployed_pods.append(pod.run())
        return deployed_pods
