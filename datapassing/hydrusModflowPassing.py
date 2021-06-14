import numpy as np
import phydrus as ph
import flopy
import constants


# TODO dowiedziec sie jakie parametry powinny tu być - prawdopodobnie shape nam dostarczy jakos info???
def updateRch():
    # read recharge value from T_LEVEL.out
    tLevel = ph.read.read_tlevel(path=constants.HYDRUS_ROOT + '\\T_LEVEL.out')
    rechargeValue = tLevel['sum(vBot)'].iat[-1]

    # load MODFLOW model - basic info and RCH package
    modflowModel = flopy.modflow.Modflow.load("simple1.nam", model_ws=constants.MODFLOW_ROOT, load_only=["rch"],
                                              forgive=True)

    # !! useful props - modflowModel.nper (stress period count), modflowModel.nrow (rows), modflowModel.ncol (cols) !!
    rchPackage = modflowModel.get_package("rch")  # get the RCH package

    # create new recharge array
    rechargeArray = np.empty((modflowModel.nrow, modflowModel.ncol))
    rechargeArray.fill(rechargeValue)  # TODO shapes handling

    stressPeriod = 0  # stress period will always be 0 (based on our notes)
    modflowModel.rch.rech[stressPeriod] = rechargeArray
    newRecharge = modflowModel.rch.rech

    # generate and save new RCH (same properties, different recharge)
    flopy.modflow.ModflowRch(modflowModel, nrchop=rchPackage.nrchop, ipakcb=rchPackage.ipakcb, rech=newRecharge,
                             irch=rchPackage.irch).write_file(check=False)


def updateWodyGruntowe():
    # TODO - the whole damn thing
    pass


updateRch()
