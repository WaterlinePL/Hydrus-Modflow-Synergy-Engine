import os.path
import re
from datapassing.hydrusModflowPassing import HydrusModflowPassing
from hydrus.hydrusMultipodDeployer import HydrusMultipodDeployer
from modflow.modflowDeployer import ModflowDeployer
from concurrent.futures import ThreadPoolExecutor
from kubernetes_controller.podController import PodController
from kubernetes.client import CoreV1Api


class Simulation:
    def __init__(self, simulation_id: int):
        self.simulation_id = simulation_id
        self.modflow_project = None
        self.loaded_shapes = None
        self.hydrus_finished = False
        self.passing_finished = False
        self.modflow_finished = False

    def run_simulation(self, api_instance: CoreV1Api, pod_controller: PodController, modflow_dir: str, hydrus_dir: str,
                       namespace: str):
        # ===== RUN HYDRUS INSTANCES ======
        hydrus_count = len(self.loaded_shapes)
        hydrus_pod_names = ["hydrus-pod-id." + str(self.simulation_id) + "-num." + str(i + 1) for i in
                            range(hydrus_count)]

        hydrus_volumes_paths = []
        for key in self.loaded_shapes:
            hydrus_volumes_paths.append(self.format_path_to_docker(dir_path=hydrus_dir, project_name=key))

        multipod_deployer = HydrusMultipodDeployer(api_instance=api_instance,
                                                   hydrus_projects_paths=hydrus_volumes_paths,
                                                   pods_names=hydrus_pod_names,
                                                   namespace=namespace)

        multipod_deployer.deploy_all()  # run all hydrus pods
        with ThreadPoolExecutor(max_workers=hydrus_count) as exe:
            exe.map(pod_controller.wait_for_pod_termination, hydrus_pod_names)

        self.hydrus_finished = True
        print('Hydrus containers finished')

        # ===== COPY RESULTS OF HYDRUS TO MODFLOW ======

        # Add hydrus result file paths (T_Level.out) to loaded_shapes (shape_file_info)
        for model_name_key in self.loaded_shapes:
            self.loaded_shapes[model_name_key].set_hydrus_recharge_output(
                os.path.join(hydrus_dir, model_name_key, "T_Level.out"))

        # Shapes list initialization from shape_file_info list
        shapes = HydrusModflowPassing.read_shapes_from_files(list(self.loaded_shapes.values()))

        # extracting modflow project .nam file
        nam_file = ""
        for file in os.listdir(os.path.join(modflow_dir, self.modflow_project)):
            if file.endswith(".nam"):
                nam_file = file
        print("Nam file", nam_file)

        result = HydrusModflowPassing(os.path.join(modflow_dir, self.modflow_project), nam_file, shapes)
        result.update_rch()

        self.passing_finished = True
        print("Passing successful")

        # ===== RUN MODFLOW INSTANCE ======

        modflow_pod_name = "modflow-2005-id." + str(self.simulation_id)
        modflow_volumes_path = self.format_path_to_docker(dir_path=modflow_dir, project_name=self.modflow_project)

        modflow_deployer = ModflowDeployer(api_instance=api_instance, path=modflow_volumes_path,
                                           name_file=nam_file, pod_name=modflow_pod_name)
        modflow_v1_pod = modflow_deployer.run_pod()  # run modflow pod
        with ThreadPoolExecutor(max_workers=1) as exe:
            exe.submit(pod_controller.wait_for_pod_termination, modflow_v1_pod.metadata.name)

        self.modflow_finished = True
        print('Modflow container finished')
        return

    def set_modflow_project(self, modflow_project) -> None:
        self.modflow_project = modflow_project

    def set_loaded_shapes(self, loaded_shapes) -> None:
        self.loaded_shapes = loaded_shapes

    def format_path_to_docker(self, dir_path: str, project_name: str) -> str:
        """
        Format windows paths to docker format "/run/desktop/mnt/host/c/..."
        @param dir_path: Path to modflow/hydrus directory
        @param project_name: Project directory name
        @return: Formatted path -> str
        """
        docker_const_path = "/run/desktop/mnt/host"
        path_split = re.split("\\\\|:\\\\", dir_path)
        path_split[0] = path_split[0].lower()
        return docker_const_path + '/' + '/'.join(path_split) + '/' + project_name

    def get_simulation_status(self):
        return self.hydrus_finished, self.passing_finished, self.modflow_finished

    def get_id(self):
        return self.simulation_id
