from kubernetes import client, config

from datapassing.hydrusModflowPassing import HydrusModflowPassing
from hydrus.hydrusMultipodDeployer import HydrusMultipodDeployer
from modflow.modflowDeployer import ModflowDeployer
from kubernetes_controller.podController import PodController
from concurrent.futures import ThreadPoolExecutor


class SimulationService:
    def __int__(self):
        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.pod_controller = PodController(self.api_instance)

    def run_simulation(self, namespace: str, hydrus_projects: [str]):  # TODO ogarnąć zmienne w funkcji
        hydrus_count = len(hydrus_projects)
        # run multiple hydrus instances and wait for them to finish
        sample_pod_names = ["hydrus-pod-" + str(i + 1) for i in range(hydrus_count)]
        multipod_deployer = HydrusMultipodDeployer(self.api_instance, hydrus_projects, sample_pod_names,
                                                   namespace=namespace)
        multipod_deployer.deploy_all()
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(self.pod_controller.wait_for_pod_termination, sample_pod_names)
        # TODO end hydrus notification
        print('Hydrus containers finished')

        # copy results of hydrus to modflow
        modflow_workspace_path = "path"
        nam_file = "file"
        shapes = []

        hydrus_modflow_passing = HydrusModflowPassing(modflow_workspace_path, nam_file, shapes)
        hydrus_modflow_passing.update_rch()
        # TODO end passing notification

        # run modflow instance and wait for it to finish
        modflow_deployer = ModflowDeployer(api_instance=self.api_instance, pod_name='modflow-2005')
        modflow_v1_pod = modflow_deployer.run_pod()
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(self.pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)
        # TODO end modflow notification
        print('Modflow container finished')
        return
