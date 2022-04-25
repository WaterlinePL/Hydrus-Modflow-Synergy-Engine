from dataclasses import dataclass, field
from typing import List, Optional
from metadata.project_step_enum import ProjectStepEnum


# Is represented as .json file in store, accessed via dao
@dataclass
class ProjectMetadata:
    name: str = None                        # name of the project, must match root catalogue
    lat: float = None                       # latitude of model
    long: float = None                      # longitude of model
    start_date: str = None                  # start date of the simulation (YYYY-mm-dd)
    end_date: str = None                    # end date of the simulation (YYYY-mm-dd)
    spin_up: float = None                   # how many days of hydrus simulation should be ignored
    rows: int = None                        # amount of rows in the model grid
    cols: int = None                        # amount of columns in the model grid
    grid_unit: str = None                   # unit in which the model grid size is represented
    row_cells: List[float] = field(default=list)        # heights of the model's consecutive rows
    col_cells: List[float] = field(default=list)        # widths of the model's consecutive columns
    modflow_model: Optional[str] = None                 # name of the folder containing the modflow model
    hydrus_models: List[str] = field(default=list)      # list of names of folders containing the hydrus models

    def remove_modflow_model(self):
        self.modflow_model = None

    def remove_hydrus_model(self, model_name: str):
        self.hydrus_models.remove(model_name)

    def get_latest_step(self) -> ProjectStepEnum:
        # TODO
        if not self.modflow_model:
            return ProjectStepEnum.MODFLOW

        if len(self.hydrus_models) == 0:
            return ProjectStepEnum.HYDRUS

    def to_json(self):
        return self.__dict__
