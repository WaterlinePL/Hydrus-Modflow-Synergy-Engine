from typing import List, Optional

import flopy.utils.util_array as flopy_array
import numpy as np
import flopy

from datapassing.shape_data import Shape


class HydrusModflowPassing:

    def __init__(self, modflow_workspace_path: str, nam_file: str, shapes: List[Shape]):

        self.modflow_workspace_path = modflow_workspace_path
        self.nam_file = nam_file
        self.shapes = shapes

    def update_rch(self, spin_up=0) -> Optional[flopy_array.Transient2d]:
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
        for idx in range(modflow_model.nper):  # i in stress periods
            recharge_modflow_array = modflow_model.rch.rech[idx].array
            for shape in self.shapes:
                mask = (shape.mask_array == 1)
                recharge_modflow_array[mask] = 0.0
                modflow_model.rch.rech[idx] = recharge_modflow_array

        for shape in self.shapes:
            sum_v_bot = shape.recharge  # get sum(vBot) values
            if spin_up >= len(sum_v_bot):
                raise ValueError('Spin up is longer than hydrus model time')
            sum_v_bot = (-np.diff(sum_v_bot))[spin_up:]  # calc differance for each day (excluding spin_up period)

            stress_period_begin = 0  # beginning of current stress period
            for idx, stress_period_duration in enumerate(modflow_model.modeltime.perlen):
                # float -> int indexing purposes
                stress_period_duration = int(stress_period_duration)

                # modflow rch array for given stress period
                recharge_modflow_array = modflow_model.rch.rech[idx].array

                # average from all hydrus sum(vBot) values during given stress period
                stress_period_end = stress_period_begin + stress_period_duration
                if stress_period_begin >= len(sum_v_bot) or stress_period_end >= len(sum_v_bot):
                    raise ValueError("Stress period " + str(idx+1) + " is out of hydrus model time")
                avg_v_bot_stress_period = np.average(sum_v_bot[stress_period_begin:stress_period_end])

                # add calculated hydrus average sum(vBot) to modflow recharge array
                recharge_modflow_array += shape.mask_array * avg_v_bot_stress_period

                # save calculated recharge to modflow model
                modflow_model.rch.rech[idx] = recharge_modflow_array

                # update beginning of current stress period
                stress_period_begin += stress_period_duration

        new_recharge = modflow_model.rch.rech
        rch_package = modflow_model.get_package("rch")  # get the RCH package

        # generate and save new RCH (same properties, different recharge)
        flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                                 irch=rch_package.irch).write_file(check=False)

        return new_recharge
