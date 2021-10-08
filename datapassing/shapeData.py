import numpy as np
import phydrus as ph


class ShapeFileData:

    def __init__(self, shape_mask_filepath: str, hydrus_output_filepath: str = None):
        if hydrus_output_filepath is not None:
            self.hydrus_recharge_output = ShapeFileData.read_hydrus_output(hydrus_output_filepath)
        self.shape_mask = ShapeFileData.read_shape_mask(shape_mask_filepath)

    @staticmethod
    def read_hydrus_output(hydrus_output_filepath) -> float:
        try:
            t_level = ph.read.read_tlevel(path=hydrus_output_filepath)
            return t_level['sum(vBot)'].iat[-1]
        except FileNotFoundError as err:
            print(f"No file found containing hydrus output: {err}")

    @staticmethod
    def read_shape_mask(shape_mask_filepath) -> np.array:
        try:
            return np.load(shape_mask_filepath)
        except FileNotFoundError as err:
            print(f"No file found containing numpy shape mask: {err}")


class Shape:

    def __init__(self, mask_array: np.array, value: float):
        self.mask_array = mask_array
        self.value = value

    def get_recharge(self) -> np.array:
        return self.mask_array * self.value