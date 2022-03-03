import re
from sys import platform

DOCKER_CONST_PATH = "/run/desktop/mnt/host"


def format_path_to_docker(dir_path: str) -> str:
    """
    Format windows paths to docker format "/run/desktop/mnt/host/c/..."
    @param dir_path: Path to modflow/hydrus project directory
    @return: Formatted path -> str
    """
    if platform == "win32":
        path_split = re.split("\\\\|:\\\\", dir_path)
        path_split[0] = path_split[0].lower()
        return DOCKER_CONST_PATH + '/' + '/'.join(path_split)
    return dir_path     # Do not change format on non-Windows OS


def convert_backslashes_to_slashes(path: str):
    return path.replace('\\', "/")


def extract_path_inside_workspace(hydrological_project_path: str) -> str:
    return hydrological_project_path.split("/water_modelling/workspace")[1]


def extract_project_name(hydrological_project_path: str) -> str:
    return extract_path_inside_workspace(hydrological_project_path).split('/')[1]


def extract_hydrological_model_name(hydrological_project_path: str) -> str:
    return extract_path_inside_workspace(hydrological_project_path).split('/')[3]


def fix_model_name(name: str):
    """
    Takes a filename string and makes it safe for further use. This method will probably need expanding.
    E.g. "modflow .1.zip" becomes "modflow__1.zip". Also file names will be truncated to 40 characters.

    @param name: the name of the file uploaded by the user
    @return: that name, made safe for the app to use
    """
    dots = name.count('.') - 1  # for when someone decides to put a dot in the filename
    name = name.replace(" ", "-").replace("_", "-").replace(".", "-", dots)  # remove problematic characters
    if len(name) > 44:  # truncate name to 40 characters long (+4 for ".zip")
        split = name.split('.')
        split[0] = split[0][0:40]
        name = ".".join(split)
    return name
