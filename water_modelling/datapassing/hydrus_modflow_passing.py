from typing import List, Tuple, Optional

import numpy as np
import flopy

from datapassing.shape_data import ShapeFileData, Shape


class HydrusModflowPassing:

    def __init__(self, modflow_workspace_path: str, nam_file: str, shapes: List[Shape]):

        self.modflow_workspace_path = modflow_workspace_path
        self.nam_file = nam_file
        self.shapes = shapes

    def update_rch(self, spin_up=0) -> Optional[np.ndarray]:
        """
        Update recharge based on shapes containing results of Hydrus simulations.
        @param spin_up: hydrus spin up period (in days)
        @return: Numpy array representing recharge (in case if it's needed)
        """
        if len(self.shapes) < 1:
            return None

        # load MODFLOW model - basic info and RCH package
        modflow_model = flopy.modflow.Modflow.load(self.nam_file, model_ws=self.modflow_workspace_path,
                                                   load_only=["rch"],
                                                   forgive=True)

        # zero all recharge values present in hydrus masks (in all stress periods)
        for idx in modflow_model.nper:  # i in stress periods
            recharge_modflow_array = modflow_model.rch.rech[idx].array
            for shape in self.shapes:
                mask = (shape.mask_array == 1)
                recharge_modflow_array[mask] = 0.0

        for shape in self.shapes:
            # get t_level values for each day excluding spin_up period
            t_level = (-np.diff(shape.get_recharge()))[spin_up:]

            stress_period_begin = 0  # beginning of current stress period
            for idx, stress_period_duration in enumerate(modflow_model.modeltime.perlen):
                # modflow rch for given stress period
                recharge_modflow_array = modflow_model.rch.rech[idx].array

                # average from all hydrus t_level values during given stress period
                t_level_stress_period = np.average(
                    t_level[stress_period_begin:stress_period_begin + stress_period_duration])

                # add calculated hydrus average t_level to modflow recharge array
                recharge_modflow_array += shape.mask_array * t_level_stress_period
                modflow_model.rch.rech[idx] = recharge_modflow_array  # save calculated recharge to modflow model

                stress_period_begin += stress_period_duration  # update beginning of current stress period

        new_recharge = modflow_model.rch.rech
        rch_package = modflow_model.get_package("rch")  # get the RCH package

        # generate and save new RCH (same properties, different recharge)
        flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                                 irch=rch_package.irch).write_file(check=False)

        return new_recharge

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
