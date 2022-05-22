from __future__ import annotations

from typing import List

from metadata.project_metadata import ProjectMetadata
from server.user_state import UserState


class TestProjectMetadataBuilder:

    def __init__(self):
        self.metadata = ProjectMetadata()
        self.metadata.name = "sample"
        self.metadata.cols = 10
        self.metadata.rows = 10
        self.metadata.long = 123.1
        self.metadata.lat = 321.3
        self.metadata.start_date = "2020-01-01"
        self.metadata.end_date = "2022-12-12"
        self.metadata.col_cells = [1.1] * 6 + [2.4] * 4
        self.metadata.row_cells = [2.1] * 3 + [1.4] * 7
        self.metadata.grid_unit = "meters"

    def modflow(self, modflow_model: str) -> TestProjectMetadataBuilder:
        self.metadata.modflow_model = modflow_model
        return self

    def add_hydrus(self, hydrus_model: str) -> TestProjectMetadataBuilder:
        self.metadata.hydrus_models.append(hydrus_model)
        return self

    def hydrus(self, hydrus_models: List[str]):
        self.metadata.hydrus_models = hydrus_models
        return self

    def spin_up(self, spin_up: int) -> TestProjectMetadataBuilder:
        self.metadata.spin_up = spin_up
        return self

