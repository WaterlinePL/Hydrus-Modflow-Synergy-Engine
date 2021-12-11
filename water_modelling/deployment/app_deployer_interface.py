from typing import List


class IAppDeployer:

    def run_hydrus(self, hydrus_dir: str, hydrus_projects: List[str], sim_id: int):
        raise Exception("Unimplemented method!")

    def run_modflow(self, modflow_dir: str, nam_file: str, sim_id: int):
        raise Exception("Unimplemented method!")
