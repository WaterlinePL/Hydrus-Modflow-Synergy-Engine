from kubernetes import client, config

from datapassing.hydrusModflowPassing import HydrusModflowPassing
from hydrus.hydrusMultipodDeployer import HydrusMultipodDeployer
from modflow.modflowDeployer import ModflowDeployer
from kubernetes_controller.podController import PodController
from concurrent.futures import ThreadPoolExecutor
import numpy as np


class SimulationService:
    def __init__(self):
        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.pod_controller = PodController(self.api_instance)

    def run_simulation(self, namespace: str, hydrus_projects: [str]):  # TODO ogarnąć zmienne w funkcji
        # ===== RUN HYDRUS INSTANCES ======
        hydrus_count = len(hydrus_projects)
        sample_pod_names = ["hydrus-pod-" + str(i + 1) for i in range(hydrus_count)]
        multipod_deployer = HydrusMultipodDeployer(self.api_instance, hydrus_projects, sample_pod_names,
                                                   namespace=namespace)
        multipod_deployer.deploy_all()
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(self.pod_controller.wait_for_pod_termination, sample_pod_names)
        # TODO end hydrus notification
        print('Hydrus containers finished')

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======
        np.save("mask1", np.array([[1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]))

        sample_shape_masks = ["masks/" + base_name for base_name in
                              ["mask1.npy", "mask2.npy", "mask3.npy", "mask4.npy"]]

        sample_hydrus_output = ["hydrus_out/" + base_name for base_name in
                                ["t_level1.out", "t_level2.out", "t_level3.out", "t_level4.out"]]

        shape_info_files = HydrusModflowPassing.create_shape_info_data(
            list(zip(sample_shape_masks, sample_hydrus_output)))

        shapes = HydrusModflowPassing.read_shapes_from_files(shape_info_files)

        result = HydrusModflowPassing("./simple1", "simple1.nam", shapes)

        result.update_rch()
        # TODO end passing notification

        # ===== RUN MODFLOW INSTANCE ======
        modflow_deployer = ModflowDeployer(api_instance=self.api_instance, pod_name='modflow-2005')
        modflow_v1_pod = modflow_deployer.run_pod()
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(self.pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)
        # TODO end modflow notification
        print('Modflow container finished')
        return

