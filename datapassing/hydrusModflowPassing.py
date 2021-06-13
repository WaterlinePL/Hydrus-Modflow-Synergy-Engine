import phydrus as ph
import flopy
import constants

#TODO dowiedziec sie jakie parametry powinny tu być - prawdopodobnie shape nam dostarczy jakos info???
def updateRch():
    # read recharge value from T_LEVEL.out
    tLevel = ph.read.read_tlevel(path=constants.HYDRUS_ROOT + '\\T_LEVEL.out')
    rechargeValue = tLevel['sum(vBot)'].iat[-1]

    # plug it into .rch and .dis (.dis is a Discretization File - it's required in all models and contains useful info)
    ml = flopy.modflow.Modflow.load("simple1.nam", model_ws=constants.MODFLOW_ROOT, load_only=["rch", "dis"],
                                    forgive=True)

    print(ml.dis.nlay)  # layer count
    print(ml.dis.nper)  # stress period count
    print(ml.dis.nrow)  # rows count
    print(ml.dis.ncol)  # cols count

    ml.rch.rech.array  # rch array 4d - [layer][stress_period][row][column]
    # TODO - update .rch


def updateWodyGruntowe():
    # TODO - the whole damn thing
    pass


updateRch()
