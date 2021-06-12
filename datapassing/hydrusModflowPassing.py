import phydrus as ph
import flopy

import constants


def updateRch():

    # read recharge value from T_LEVEL.out
    tLevel = ph.read.read_tlevel(path=constants.HYDRUS_ROOT + '\\T_LEVEL.out')
    rechargeValue = tLevel['sum(vBot)'].iat[-1]

    # plug it into .rch
    ml = flopy.modflow.Modflow.load("simple1.nam", model_ws=constants.MODFLOW_ROOT, load_only=["rch"], forgive=True)
    # TODO - update .rch


def updateWodyGruntowe():
    # TODO - the whole damn thing
    pass
