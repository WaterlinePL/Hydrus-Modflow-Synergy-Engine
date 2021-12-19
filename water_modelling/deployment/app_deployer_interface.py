from typing import List, Optional

from simulation.simulation_error import SimulationError


class IAppDeployer:

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int) -> List[SimulationError]:
        raise Exception("Unimplemented method!")

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id: int) -> Optional[SimulationError]:
        raise Exception("Unimplemented method!")
