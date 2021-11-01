from kubernetes import client, config
from kubernetes_controller.pod_controller import PodController
from simulation.simulation import Simulation


class SimulationService:
    def __init__(self, hydrus_dir: str, modflow_dir: str):
        config.load_kube_config()
        self.api_instance = client.CoreV1Api()
        self.hydrus_dir = hydrus_dir
        self.modflow_dir = modflow_dir
        self.pod_controller = PodController(self.api_instance)
        self.simulations = []

    def prepare_simulation(self) -> Simulation:
        sim_id = len(self.simulations)
        simulation = Simulation(simulation_id=sim_id)
        self.simulations.append({'simulation': simulation, 'is_finished': False})
        return simulation

    def run_simulation(self, simulation_id: int, namespace: str) -> None:
        self.simulations[simulation_id]['simulation'].run_simulation(self.api_instance, self.pod_controller,
                                                                     self.modflow_dir,
                                                                     self.hydrus_dir, namespace)

    def check_simulation_status(self, simulation_id: int):
        hydrus_done, passing_done, modflow_done = self.simulations[simulation_id]['simulation'].get_simulation_status()
        if hydrus_done and passing_done and modflow_done:
            self.simulations[simulation_id]['is_finished'] = True
        return hydrus_done, passing_done, modflow_done
