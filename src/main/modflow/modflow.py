import flopy
import os

model_ws = os.path.join("/tmp", "")
model_dir = os.path.abspath(os.path.join(os.getcwd(), model_ws))
MODFLOW_PATH = "PATH_TO_MODFLOW"
NAM_FILE = "etsdrt.nam"


ml = flopy.modflow.Modflow.load(NAM_FILE, model_ws=model_ws, load_only=None, forgive=False, exe_name=MODFLOW_PATH)
ml.run_model()

