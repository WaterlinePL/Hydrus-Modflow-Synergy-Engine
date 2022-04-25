import os.path
from typing import List

import numpy as np
import phydrus as ph
import app_config.deployment_config as deployment_config


class ShapeMetadata:
    MASK_FILETYPE = ".np"

    def __init__(self, shape_mask_array: np.ndarray, main_project_name: str, hydrus_model_name: str):
        """
        This class contains metadata stored for defining and presenting shape masks to the user in UI.
        @param shape_mask_array: NumPy 2D array representing bitmask of a particular shape
        """
        self.shape_mask = shape_mask_array
        self.model_name = main_project_name
        self.hydrus_model_name = hydrus_model_name

    # TODO: migrate to MaskDao (and make it)
    def dump_to_file(self):
        path = os.path.join(deployment_config.WORKSPACE_DIR,
                            self.model_name,
                            self.hydrus_model_name)
        file = path + ShapeMetadata.MASK_FILETYPE
        self.shape_mask.dump(file)


class Shape:

    def __init__(self, mask_array: np.ndarray, hydrus_output_filepath: str):
        """
        This class contains shape data used for passing output of Hydrus (recharge) as an input of Modflow.
        @param mask_array: NumPy 2D array representing bitmask of a particular shape
        @param hydrus_output_filepath: Path to the Hydrus output file - T_Level.out containing 'sum vBot' (recharge)
        """
        self.mask_array = mask_array
        self.recharge = Shape._read_hydrus_output(hydrus_output_filepath)

    @staticmethod
    def _read_hydrus_output(hydrus_output_filepath: str) -> List[float]:
        """
        Read Hydrus simulation output from file T_Level.out (read all entries of sum(vBot))
        @param hydrus_output_filepath: Path to T_Level.out
        @return:
        """
        try:
            t_level = ph.read.read_tlevel(path=hydrus_output_filepath)
            return t_level['sum(vBot)']
        except FileNotFoundError as err:
            print(f"No file found containing hydrus output: {err}")
