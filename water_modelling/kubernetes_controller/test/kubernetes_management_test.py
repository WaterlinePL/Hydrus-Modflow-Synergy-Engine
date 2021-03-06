import unittest
from kubernetes import client, config
from hydrus.kubernetes.hydrus_job_deployer import _HydrusJobDeployer
from hydrus.desktop.hydrus_multi_deployer import HydrusLocalMultiDeployer
from modflow.modflow_job_deployer import ModflowPodDeployer
from constants import HYDRUS_ROOT_DOCKER
from kubernetes_controller.job_controller import JobController
from concurrent.futures import ThreadPoolExecutor


class KubernetesManagementTest(unittest.TestCase):

    def test_modflow_delete(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()

        modflow_deployer = ModflowPodDeployer(api_instance=api_instance, pod_name='modflow-2005')
        modflow_v1_pod = modflow_deployer.run()  # returns V1Pod instance

        pod_controller = JobController(api_instance)
        pod_controller.wait_for_pod_termination(modflow_v1_pod.metadata.name)

    def test_hydrus_delete(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()

        hydrus_deployer = _HydrusJobDeployer(api_instance=api_instance, sub_path=HYDRUS_ROOT_DOCKER, job_name='hydrus-1d')
        hydrus_pod = hydrus_deployer.run()  # returns V1Pod instance

        pod_controller = JobController(api_instance)
        pod_controller.wait_for_pod_termination(hydrus_pod.metadata.name)

    def test_sequence_delete(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        pod_controller = JobController(api_instance)

        print("Deploying modflow container")
        modflow_deployer = ModflowPodDeployer(api_instance=api_instance, pod_name='modflow-2005')
        modflow_v1_pod = modflow_deployer.run()  # returns V1Pod instance
        pod_controller.wait_for_pod_termination(modflow_v1_pod.metadata.name)

        print("Deploying hydrus container")
        hydrus_deployer = _HydrusJobDeployer(api_instance=api_instance, sub_path=HYDRUS_ROOT_DOCKER, job_name='hydrus-1d')
        hydrus_pod = hydrus_deployer.run()  # returns V1Pod instance
        pod_controller.wait_for_pod_termination(hydrus_pod.metadata.name)

    def test_shapes_usage(self):
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        pod_controller = JobController(api_instance)

        namespace = "default"
        sample_pod_names = ["hydrus-pod-" + str(i + 1) for i in range(4)]
        hydrus_project_path = HYDRUS_ROOT_DOCKER
        hydrus_projects = [hydrus_project_path for _ in range(4)]

        multipod_deployer = HydrusLocalMultiDeployer(api_instance, hydrus_projects, sample_pod_names, namespace=namespace)
        multipod_deployer.run()
        with ThreadPoolExecutor(max_workers=4) as exe:
            exe.map(pod_controller.wait_for_pod_termination, sample_pod_names)
        print('Hydrus containers finished')

        modflow_deployer = ModflowPodDeployer(api_instance=api_instance, pod_name='modflow-2005')
        modflow_v1_pod = modflow_deployer.run()
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)
        print('Modflow container finished')

    def test_threaded_delete(self):
        with ThreadPoolExecutor(max_workers=4) as exe:
            results = exe.map(KubernetesManagementTest.chain, ([1, 2, 3, 4]))

        for r in results:
            print(r)

    @staticmethod
    def chain(n) -> None:
        config.load_kube_config()
        api_instance = client.CoreV1Api()
        pod_controller = JobController(api_instance)

        hydrus_deployer = _HydrusJobDeployer(api_instance=api_instance, sub_path=HYDRUS_ROOT_DOCKER,
                                             job_name='hydrus-1d' + str(n))
        hydrus_pod = hydrus_deployer.run()  # returns V1Pod instance
        pod_controller.wait_for_pod_termination(hydrus_pod.metadata.name)

        modflow_deployer = ModflowPodDeployer(api_instance=api_instance, pod_name='modflow-2005' + str(n))
        modflow_v1_pod = modflow_deployer.run()  # returns V1Pod instance
        pod_controller.wait_for_pod_termination(modflow_v1_pod.metadata.name)

        return 'Chain ' + str(n) + ' finished'


if __name__ == '__main__':
    unittest.main()
