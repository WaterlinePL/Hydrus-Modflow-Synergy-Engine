from enum import Enum


class ProjectStepEnum(Enum):
    MODFLOW = 1
    HYDRUS = 2
    MASKING = 3
    SIMULATION = 4
