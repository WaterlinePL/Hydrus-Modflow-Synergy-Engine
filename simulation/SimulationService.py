import os.path
import re

from kubernetes import client, config

from datapassing.hydrusModflowPassing import HydrusModflowPassing
from hydrus.hydrusMultipodDeployer import HydrusMultipodDeployer
from modflow.modflowDeployer import ModflowDeployer
from kubernetes_controller.podController import PodController
from concurrent.futures import ThreadPoolExecutor


# TODO REFACTOR
class SimulationService:
    def __init__(self, hydrus_dir: str, modflow_dir: str, modflow_project: str, loaded_shapes: dict):
        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.hydrus_dir = hydrus_dir
        self.modflow_dir = modflow_dir
        self.modflow_project = modflow_project
        self.loaded_shapes = loaded_shapes
        self.pod_controller = PodController(self.api_instance)

    def run_simulation(self, Id: int, namespace: str):
        # ===== RUN HYDRUS INSTANCES ======
        hydrus_count = len(self.loaded_shapes)
        hydrus_pod_names = ["hydrus-pod-id." + str(Id) + "-num." + str(i + 1) for i in range(hydrus_count)]

        # Zmiana ścieżki z windowsowej na dockerowe "/run/desktop/mnt/host/c/..."
        docker_const_path = "/run/desktop/mnt/host"
        hydrus_path_splited = re.split("\\\\|:\\\\", self.hydrus_dir)
        hydrus_path_splited[0] = hydrus_path_splited[0].lower()
        hydrus_path_to_dir_docker = docker_const_path + '/' + '/'.join(hydrus_path_splited)
        hydrus_project_paths = []
        for key in self.loaded_shapes:
            hydrus_project_paths.append(hydrus_path_to_dir_docker + '/' + key)

        multipod_deployer = HydrusMultipodDeployer(api_instance=self.api_instance,
                                                   hydrus_projects_paths=hydrus_project_paths,
                                                   pods_names=hydrus_pod_names,
                                                   namespace=namespace)

        multipod_deployer.deploy_all()
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(self.pod_controller.wait_for_pod_termination, hydrus_pod_names)

        # TODO end hydrus notification
        print('Hydrus containers finished')

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======

        # dodanie ścieżek gdzie będą wyniki hydrusa (T_Level.out)
        for model_name_key in self.loaded_shapes:
            self.loaded_shapes[model_name_key].set_hydrus_recharge_output(os.path.join(self.hydrus_dir, model_name_key, "T_Level.out"))
            print(model_name_key, "->", self.loaded_shapes[model_name_key].hydrus_recharge_output, self.loaded_shapes[model_name_key].shape_mask,)

        # stworzenie shape'ów
        shapes = HydrusModflowPassing.read_shapes_from_files(list(self.loaded_shapes.values()))

        # wyciągnięcie nam_file'a
        nam_file = ""
        for file in os.listdir(os.path.join(self.modflow_dir, self.modflow_project)):
            if file.endswith(".nam"):
                nam_file = file
        print("Nam file", nam_file)

        result = HydrusModflowPassing(os.path.join(self.modflow_dir, self.modflow_project), nam_file, shapes)
        result.update_rch()

        # TODO end passing notification
        print("Passing successful")

        # ===== RUN MODFLOW INSTANCE ======

        modflow_pod_name = "modflow-2005-id." + str(Id)  # TODO PATH mounta modflowa

        # Zmiana ścieżki z windowsowej na dockerowe "/run/desktop/mnt/host/c/..."
        modflow_path_splited = re.split("\\\\|:\\\\", self.modflow_dir)
        modflow_path_splited[0] = modflow_path_splited[0].lower()
        modflow_mount_path = docker_const_path + '/' + '/'.join(modflow_path_splited) + '/' + self.modflow_project

        modflow_deployer = ModflowDeployer(api_instance=self.api_instance, path=modflow_mount_path, pod_name=modflow_pod_name)
        modflow_v1_pod = modflow_deployer.run_pod()
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(self.pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)

        # TODO end modflow notification
        print('Modflow container finished')
        return
