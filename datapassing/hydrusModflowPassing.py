import numpy as np
import phydrus as ph
import flopy
import constants


# TODO dowiedziec sie jakie parametry powinny tu być - prawdopodobnie shape nam dostarczy jakos info???
def updateRch():
    # read recharge value from T_LEVEL.out
    t_level = ph.read.read_tlevel(path=constants.HYDRUS_ROOT + '\\T_LEVEL.out')
    recharge_value = t_level['sum(vBot)'].iat[-1]

    # load MODFLOW model - basic info and RCH package
    modflow_model = flopy.modflow.Modflow.load("simple1.nam", model_ws=constants.MODFLOW_ROOT, load_only=["rch"],
                                               forgive=True)

    # !! useful props:
    # modflow_model.nper (stress period count),
    # modflow_model.nrow (rows),
    # modflow_model.ncol (cols) !!
    rch_package = modflow_model.get_package("rch")  # get the RCH package

    # create new recharge array
    recharge_array = np.empty((modflow_model.nrow, modflow_model.ncol))
    recharge_array.fill(recharge_value)  # TODO shapes handling

    stress_period = 0  # stress period will always be 0 (based on our notes)
    modflow_model.rch.rech[stress_period] = recharge_array
    new_recharge = modflow_model.rch.rech

    # generate and save new RCH (same properties, different recharge)
    flopy.modflow.ModflowRch(modflow_model, nrchop=rch_package.nrchop, ipakcb=rch_package.ipakcb, rech=new_recharge,
                             irch=rch_package.irch).write_file(check=False)


# No i co by powiedział Testoviron jakby zobaczył polskie słowa w kodzie
def updateWodyGruntowe():
    # TODO - the whole damn thing
    pass


updateRch()
