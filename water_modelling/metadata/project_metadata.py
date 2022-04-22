from typing import List, Optional
from project_step_enum import ProjectStepEnum


# Is represented as .json file in store, accessed via dao
class ProjectMetadata:
    name: str                       # name of the project, must match root catalogue
    lat: float                      # latitude of model
    long: float                     # longitude of model
    start_date: str                 # start date of the simulation (YYYY-mm-dd)
    end_date: str                   # end date of the simulation (YYYY-mm-dd)
    spin_up: float                  # how many days of hydrus simulation should be ignored
    rows: int                       # amount of rows in the model grid
    cols: int                       # amount of columns in the model grid
    grid_unit: str                  # unit in which the model grid size is represented
    row_cells: List[float]          # heights of the model's consecutive rows
    col_cells: List[float]          # widths of the model's consecutive columns
    modflow_model: Optional[str]    # name of the folder containing the modflow model
    hydrus_models: List[str]        # list of names of folders containing the hydrus models

    def __init__(self):
        # TODO
        pass

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
        pass
