from app_config import deployment_config
from simulation.simulation import Simulation


class SimulationService:
    def __init__(self, hydrus_dir: str, modflow_dir: str):
        self.hydrus_dir = hydrus_dir
        self.modflow_dir = modflow_dir
        self.deployer = deployment_config.DEPLOYER
        self.simulations = []

    def prepare_simulation(self) -> Simulation:
        sim_id = len(self.simulations)
        simulation = Simulation(simulation_id=sim_id, deployer=self.deployer)
        self.simulations.append({'simulation': simulation, 'is_finished': False})
        return simulation

    def run_simulation(self, simulation_id: int) -> None:
        self.simulations[simulation_id]['simulation'].run_simulation(self.modflow_dir, self.hydrus_dir)

    def check_simulation_status(self, simulation_id: int):
        hydrus_done, passing_done, modflow_done = self.simulations[simulation_id]['simulation'].get_simulation_status()
        if hydrus_done and passing_done and modflow_done:
            self.simulations[simulation_id]['is_finished'] = True
        return hydrus_done, passing_done, modflow_done
