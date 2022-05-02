import os
import numpy as np

from app_config import deployment_config
from datapassing.shape_data import ShapeMetadata

MASK_FILETYPE = ".npy"


def get(project_name: str, hydrus_model_name: str):
    mask = np.load(_get_mask_filename(project_name, hydrus_model_name))
    return ShapeMetadata(mask, project_name, hydrus_model_name)


def save_or_update(mask: ShapeMetadata):
    path = _get_mask_filename(mask.project_name, mask.hydrus_model_name)
    np.save(path, mask.shape_mask)


def delete(mask: ShapeMetadata):
    os.remove(_get_mask_filename(mask.project_name, mask.hydrus_model_name))


def _get_mask_filename(project_name: str, hydrus_model_name: str) -> str:
    # workspace/<project>/hydrus/<model>/<model>.npy
    return os.path.join(deployment_config.WORKSPACE_DIR,
                        project_name,
                        "hydrus",
                        hydrus_model_name,
                        hydrus_model_name + MASK_FILETYPE)
