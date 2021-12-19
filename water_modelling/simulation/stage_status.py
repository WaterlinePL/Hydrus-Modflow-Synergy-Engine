from typing import List


class SimulationStageStatus:

    def __init__(self):
        self._ended = False
        self._errors: List[Exception] = []

    def has_ended(self) -> bool:
        return self._ended

    def get_errors(self) -> List[Exception]:
        return self._errors

    def add_error(self, error: Exception):
        self._errors.append(error)

    def set_ended(self, ended: bool):
        self._ended = ended


