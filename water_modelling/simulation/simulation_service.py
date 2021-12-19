from typing import Tuple, List

from app_config import deployment_config
from simulation.simulation import Simulation
from simulation.stage_status import SimulationStageStatus


class SimulationService:
    def __init__(self, hydrus_dir: str, modflow_dir: str):
        self.hydrus_dir = hydrus_dir
        self.modflow_dir = modflow_dir
        self.deployer = deployment_config.DEPLOYER
        self.simulations: List[Simulation] = []

    def prepare_simulation(self) -> Simulation:
        sim_id = len(self.simulations)
        simulation = Simulation(simulation_id=sim_id, deployer=self.deployer)
        self.simulations.append(simulation)
        return simulation

    def run_simulation(self, simulation_id: int) -> None:
        self.simulations[simulation_id].run_simulation(self.modflow_dir, self.hydrus_dir)

    def check_simulation_status(self, simulation_id: int) -> Tuple[SimulationStageStatus,
                                                                   SimulationStageStatus,
                                                                   SimulationStageStatus]:
        """
        Return status of each step in particular simulation.
        @param simulation_id: Id of the simulation to check
        @return: Status of hydrus stage, passing stage and modflow stage (in this exact order)
        """

        hydrus_stage_status = self.simulations[simulation_id].get_hydrus_stage_status()
        passing_stage_status = self.simulations[simulation_id].get_passing_stage_status()
        modflow_stage_status = self.simulations[simulation_id].get_modflow_stage_status()

        if hydrus_stage_status and passing_stage_status and modflow_stage_status:
            self.simulations[simulation_id].finished = True

        return hydrus_stage_status, passing_stage_status, modflow_stage_status
