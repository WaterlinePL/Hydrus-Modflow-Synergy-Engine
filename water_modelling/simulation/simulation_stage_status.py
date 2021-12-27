from typing import List

from simulation.simulation_error import SimulationError


class SimulationStageStatus:

    def __init__(self):
        self._ended = False
        self._errors: List[SimulationError] = []

    def get_errors(self) -> List[SimulationError]:
        return self._errors

    def has_ended(self) -> bool:
        return self._ended

    def add_error(self, error: SimulationError):
        self._errors.append(error)

    def set_ended(self, ended: bool):
        self._ended = ended


