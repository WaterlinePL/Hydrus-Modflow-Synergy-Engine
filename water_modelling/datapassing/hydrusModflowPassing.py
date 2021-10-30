from typing import List, Tuple, Optional

import numpy as np
import flopy

from datapassing.shapeData import ShapeFileData, Shape


class HydrusModflowPassing:

    def __init__(self, modflow_workspace_path: str, nam_file: str, shapes: List[Shape]):

        self.modflow_workspace_path = modflow_workspace_path
        self.nam_file = nam_file
        self.shapes = shapes

    def update_rch(self, stress_period: int = 0) -> Optional[np.ndarray]:
        """
        Update recharge based on shapes containing results of Hydrus simulations.
        @param stress_period: Number of stress period (timeline period?)
        @return: Numpy array representing recharge (in case if it's needed)
        """
        if len(self.shapes) < 1:
            return None

        # load MODFLOW model - basic info and RCH package
        modflow_model = flopy.modflow.Modflow.load(self.nam_file, model_ws=self.modflow_workspace_path,
                                                   load_only=["rch"],
                                                   forgive=True)

        recharge = modflow_model.rch.rech[stress_period].array

        for shape in self.shapes:
            mask = (shape.mask_array == 1)
            recharge[mask] = 0.0

        for shape in self.shapes:
            recharge += shape.get_recharge()


        # !! useful props:
        # modflow_model.nper (stress period count),
        # modflow_model.nrow (rows),
        # modflow_model.ncol (cols) !!
        rch_package = modflow_model.get_package("rch")  # get the RCH package

        # create new recharge array
        modflow_model.rch.rech[stress_period] = recharge
        new_recharge = modflow_model.rch.rech

        # generate and save new RCH (same properties, different recharge)
        flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                                 irch=rch_package.irch).write_file(check=False)

        return recharge

    @staticmethod
    def read_shapes_from_files(shape_info_files: List[ShapeFileData]) -> List[Shape]:
        """
        Read Modflow shape data from Hydrus output files and masks (metadata) and convert it to Shape class instances
        @param shape_info_files: List of metadata (contains Hydrus model and mask info)
        @return: List of shapes (Shape class instances) with info about mask and result of Hydrus simulation
        """

        shapes = []
        for shape_info in shape_info_files:
            shapes.append(Shape(
                shape_info.shape_mask,
                shape_info.hydrus_recharge_output
            ))
        return shapes

    # FIXME: probably useless
    @staticmethod
    def create_shape_info_data(shape_data_files: List[Tuple[str, str]]) -> List[ShapeFileData]:
        shape_info_files = []
        for shape_mask_file, hydrus_output_file in shape_data_files:
            shape_info_files.append(ShapeFileData(
                shape_mask_file,
                hydrus_output_file
            ))
        return shape_info_files
