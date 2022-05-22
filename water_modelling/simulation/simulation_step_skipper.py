import os

from app_config import deployment_config
from metadata.project_metadata import ProjectMetadata


# TODO: Get latest possible step

def _check_modflow_skip(project: ProjectMetadata):
    return project.modflow_model is not None


def _check_hydrus_skip(project: ProjectMetadata):
    return len(project.hydrus_models) > 0


def _check_shapes_skip(project: ProjectMetadata):
    project_dir = os.path.join(deployment_config.WORKSPACE_DIR, project.name)
    project_files = os.listdir(project_dir)
    for file in project_files:
        # TODO: check if there is a Hydrus project matching such mask
        if file.endswith(deployment_config.MASK_FILETYPE):  # If we find any mask file, masking can be skipped
            return True
    return False
