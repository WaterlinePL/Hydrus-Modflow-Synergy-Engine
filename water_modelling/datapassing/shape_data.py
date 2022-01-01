from typing import List

import numpy as np
import phydrus as ph


class ShapeFileData:

    def __init__(self, shape_mask_array: np.ndarray = None):

        if hydrus_output_filepath is not None:
            self.hydrus_recharge_output = ShapeFileData.read_hydrus_output(hydrus_output_filepath)

        if hydrus_output_filepath is not None:
            self.shape_mask = ShapeFileData.read_shape_mask(shape_mask_filepath)
        elif shape_mask_array is not None:
            self.shape_mask = shape_mask_array

    @staticmethod
    def read_hydrus_output(hydrus_output_filepath: str) -> List[float]:
        """
        Read Hydrus simulation output from file T_Level.out (read all entries of sum(vBot))
        @param hydrus_output_filepath: P
        @return:
        """
        try:
            t_level = ph.read.read_tlevel(path=hydrus_output_filepath)
            return t_level['sum(vBot)']
        except FileNotFoundError as err:
            print(f"No file found containing hydrus output: {err}")

    def set_hydrus_recharge_output(self, hydrus_output_filepath: str):
        self.hydrus_recharge_output = ShapeFileData.read_hydrus_output(hydrus_output_filepath)


class Shape:

    def __init__(self, mask_array: np.array, values: List[float]):
        self.mask_array = mask_array
        self.values = values

    def get_mask(self) -> np.array:
        return self.mask_array

    def get_recharge(self) -> List[float]:
        return self.values
