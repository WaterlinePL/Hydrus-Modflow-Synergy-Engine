from typing import List, Tuple

import numpy as np
import phydrus as ph
import flopy
import constants


class ShapeFileData:

    def __init__(self, shape_mask_filepath: str, hydrus_output_filepath: str):
        self.shape_mask_filepath = shape_mask_filepath
        self.hydrus_output_filepath = hydrus_output_filepath

    def read_hydrus_output(self) -> float:
        t_level = ph.read.read_tlevel(path=self.hydrus_output_filepath)
        return t_level['sum(vBot)'].iat[-1]

    def read_shape_mask(self) -> np.array:
        return np.load(self.shape_mask_filepath)


class Shape:

    def __init__(self, mask_array: np.array, value: float):
        self.mask_array = mask_array
        self.value = value

    def get_recharge(self) -> np.array:
        return self.mask_array * self.value


class HydrusModflowPassing:

    def __init__(self,
                 modflow_workspace_path: str,
                 nam_file: str,
                 shapes: List[Shape]):

        self.modflow_workspace_path = modflow_workspace_path
        self.nam_file = nam_file
        self.shapes = shapes

    def update_rch(self, stress_period: int = 0) -> np.array:

        if len(self.shapes) < 1:
            return None

        modflow_model = flopy.modflow.Modflow.load(self.nam_file, model_ws=self.modflow_workspace_path, load_only=["rch"],
                                                   forgive=True)
        recharge = np.zeros((modflow_model.nrow, modflow_model.ncol))

        for shape in self.shapes:
            recharge += shape.get_recharge()

        # load MODFLOW model - basic info and RCH package

        # !! useful props:
        # modflow_model.nper (stress period count),
        # modflow_model.nrow (rows),
        # modflow_model.ncol (cols) !!
        rch_package = modflow_model.get_package("rch")  # get the RCH package

        # create new recharge array
        # recharge_array.fill(recharge_value)  # TODO shapes handling - done?

        modflow_model.rch.rech[stress_period] = recharge
        new_recharge = modflow_model.rch.rech

        # generate and save new RCH (same properties, different recharge)
        flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                                 irch=rch_package.irch).write_file(check=False)

        return recharge

    @staticmethod
    def read_shapes_from_files(shape_info_files: List[ShapeFileData]) -> List[Shape]:
        shapes = []
        for shape_info in shape_info_files:
            shapes.append(Shape(
                shape_info.read_shape_mask(),
                shape_info.read_hydrus_output()
            ))
        return shapes

    @staticmethod
    def create_shape_info_data(shape_data_files: List[Tuple[str, str]]) -> List[ShapeFileData]:
        shape_info_files = []
        for shape_mask_file, hydrus_output_file in shape_data_files:
            shape_info_files.append(ShapeFileData(
                shape_mask_file,
                hydrus_output_file
            ))
        return shape_info_files

    def update_wody_gruntowe(self):
        # TODO - the whole damn thing
        pass
