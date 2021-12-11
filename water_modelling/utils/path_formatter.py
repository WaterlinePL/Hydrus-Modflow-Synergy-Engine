import re
from sys import platform

DOCKER_CONST_PATH = "/run/desktop/mnt/host"


def format_path_to_docker(dir_path: str) -> str:
    """
    Format windows paths to docker format "/run/desktop/mnt/host/c/..."
    @param dir_path: Path to modflow/hydrus project directory
    @return: Formatted path -> str
    """

    path_split = re.split("\\\\|:\\\\", dir_path)
    path_split[0] = path_split[0].lower()
    return DOCKER_CONST_PATH + '/' + '/'.join(path_split)


def convert_backslashes_to_slashes(path: str):
    return path.replace('\\', "/")
