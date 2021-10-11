import os.path
import re

from kubernetes import client, config

from datapassing.hydrusModflowPassing import HydrusModflowPassing
from hydrus.hydrusMultipodDeployer import HydrusMultipodDeployer
from modflow.modflowDeployer import ModflowDeployer
from kubernetes_controller.podController import PodController
from concurrent.futures import ThreadPoolExecutor


class SimulationService:
    def __init__(self, hydrus_dir: str, modflow_dir: str, modflow_project: str, loaded_shapes: dict):
        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.hydrus_dir = hydrus_dir
        self.modflow_dir = modflow_dir
        self.modflow_project = modflow_project
        self.loaded_shapes = loaded_shapes
        self.pod_controller = PodController(self.api_instance)

    def run_simulation(self, simulation_id: int, namespace: str):
        # ===== RUN HYDRUS INSTANCES ======
        hydrus_count = len(self.loaded_shapes)
        hydrus_pod_names = ["hydrus-pod-id." + str(simulation_id) + "-num." + str(i + 1) for i in range(hydrus_count)]

        hydrus_volumes_paths = []
        for key in self.loaded_shapes:
            hydrus_volumes_paths.append(format_path_to_docker(dir_path=self.hydrus_dir, project_name=key))

        multipod_deployer = HydrusMultipodDeployer(api_instance=self.api_instance,
                                                   hydrus_projects_paths=hydrus_volumes_paths,
                                                   pods_names=hydrus_pod_names,
                                                   namespace=namespace)

        multipod_deployer.deploy_all()  # run all hydrus pods
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(self.pod_controller.wait_for_pod_termination, hydrus_pod_names)

        # TODO end hydrus notification
        print('Hydrus containers finished')

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======

        # Add hydrus result file paths (T_Level.out) to loaded_shapes (shape_file_info)
        for model_name_key in self.loaded_shapes:
            self.loaded_shapes[model_name_key].set_hydrus_recharge_output(
                os.path.join(self.hydrus_dir, model_name_key, "T_Level.out"))

        # Shapes list initialization from shape_file_info list
        shapes = HydrusModflowPassing.read_shapes_from_files(list(self.loaded_shapes.values()))

        # extracting modflow project .nam file
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

        modflow_pod_name = "modflow-2005-id." + str(simulation_id)
        modflow_volumes_path = format_path_to_docker(dir_path=self.modflow_dir, project_name=self.modflow_project)

        modflow_deployer = ModflowDeployer(api_instance=self.api_instance, path=modflow_volumes_path,
                                           name_file=nam_file, pod_name=modflow_pod_name)
        modflow_v1_pod = modflow_deployer.run_pod()  # run modflow pod
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(self.pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)

        # TODO end modflow notification
        print('Modflow container finished')
        return


def format_path_to_docker(dir_path: str, project_name: str) -> str:
    """
    Format windows paths to docker format "/run/desktop/mnt/host/c/..."
    @param dir_path: Path to modflow/hydrus directory
    @param project_name: Project directory name
    @return: Formatted path -> str
    """
    docker_const_path = "/run/desktop/mnt/host"
    modflow_path_split = re.split("\\\\|:\\\\", dir_path)
    modflow_path_split[0] = modflow_path_split[0].lower()
    return docker_const_path + '/' + '/'.join(modflow_path_split) + '/' + project_name
