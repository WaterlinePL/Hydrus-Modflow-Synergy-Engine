import time
import unittest
from typing import List

from kubernetes import client, config
from kubernetes.client import V1Pod

from constants import HYDRUS_ROOT_DOCKER
from hydrus.hydrus_multi_deployer import HydrusMultiDeployer

CONTAINER_NAME = "hydrus1d_linux:latest"


class HydrusPodsTest(unittest.TestCase):

    def test_four_pods(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        namespace = "default"
        sample_pod_names = ["hydrus-pod-" + str(i + 1) for i in range(4)]
        hydrus_project_path = HYDRUS_ROOT_DOCKER
        hydrus_projects = [hydrus_project_path for _ in range(4)]

        multipod_deployer = HydrusMultiDeployer(api_instance, hydrus_projects, sample_pod_names, namespace=namespace)
        multipod_deployer.run()

        print("Waiting for all pods to complete their jobs")
        job_done = False
        while not job_done:
            job_done = True
            time.sleep(5)
            pods_info = api_instance.list_pod_for_all_namespaces(watch=False)
            print("--------------")
            for pod in pods_info.items:
                HydrusPodsTest.print_single_pod(pod)
                if HydrusPodsTest.check_container_name(pod) \
                        and pod.status.container_statuses[0].state.terminated is None:
                    job_done = False

        pods_info = api_instance.list_pod_for_all_namespaces(watch=False)
        HydrusPodsTest.print_terminated_pods(pods_info.items)

        for pod in pods_info.items:
            if HydrusPodsTest.check_container_name(pod):
                self.assertEqual(pod.status.container_statuses[0].state.terminated.reason, "Completed")

        HydrusPodsTest.delete_pods(api_instance, namespace, sample_pod_names)

    @staticmethod
    def check_container_name(pod: V1Pod):
        return pod.status.container_statuses[0].image == CONTAINER_NAME

    @staticmethod
    def delete_pods(api_instance: client.CoreV1Api, namespace: str, pod_names: List[str]):
        print("Deleting test pods...")
        for name in pod_names:
            api_instance.delete_namespaced_pod(name, namespace)
        print("Test pods have been deleted.")

    @staticmethod
    def print_terminated_pods(pods: List[V1Pod]):
        print()
        print("=====================")
        print()
        print("All containers finished their jobs: ")
        HydrusPodsTest.print_pods(pods)

    @staticmethod
    def print_pods(pods: List[V1Pod]):
        for pod_data in pods:
            HydrusPodsTest.print_single_pod(pod_data)

    @staticmethod
    def print_single_pod(pod: V1Pod):
        if pod.status.container_statuses[0].state.running is not None:
            state = "Running"
        elif pod.status.container_statuses[0].state.terminated is not None:
            state = pod.status.container_statuses[0].state.terminated.reason
        elif pod.status.container_statuses[0].state.waiting is not None:
            state = "Waiting!"
        else:
            state = "unknown"
        print("%s\t\t%s\t%s\t\t\t state: %s" % (pod.status.pod_ip, pod.metadata.namespace, pod.metadata.name, state))


if __name__ == '__main__':
    unittest.main()
