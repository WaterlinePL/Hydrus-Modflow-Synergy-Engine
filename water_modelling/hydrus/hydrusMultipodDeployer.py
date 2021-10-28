from typing import List

from kubernetes import client

from hydrus.hydrusDeployer import HydrusDeployer


class HydrusMultipodDeployer:

    def __init__(self, api_instance: client.CoreV1Api, hydrus_projects_paths: List[str], pods_names: List[str],
                 namespace: str = ' default'):
        self.hydrus_pods = []
        for i, path in enumerate(hydrus_projects_paths):
            self.hydrus_pods.append(HydrusDeployer(api_instance, path, pods_names[i], namespace=namespace))

    def deploy_all(self):
        deployed_pods = []
        for pod in self.hydrus_pods:
            deployed_pods.append(pod.run_pod())
        return deployed_pods
