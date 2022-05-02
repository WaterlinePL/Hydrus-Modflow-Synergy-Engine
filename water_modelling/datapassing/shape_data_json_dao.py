import os
from typing import Dict, Optional

import numpy as np

from app_config import deployment_config
from datapassing.shape_data import ShapeMetadata

HydrusModelName = str

MASK_FILETYPE = ".npy"


def wipe_all_masks(project_name: str):
    hydrus_models_path = os.path.join(deployment_config.WORKSPACE_DIR, project_name, "hydrus")
    for hydrus_model_name in os.listdir(hydrus_models_path):
        try:
            delete(project_name, hydrus_model_name)
        except FileNotFoundError:
            pass    # If no mask found - not a problem, probably nothing to remove


def scan_for_mask_in_project(project_name: str) -> Dict[HydrusModelName, ShapeMetadata]:
    models_to_masks = {}
    hydrus_models_path = os.path.join(deployment_config.WORKSPACE_DIR, project_name, "hydrus")
    for hydrus_model_name in os.listdir(hydrus_models_path):
        try:
            mask_metadata = get(project_name, hydrus_model_name)
            models_to_masks[hydrus_model_name] = mask_metadata
        except FileNotFoundError:
            pass    # If no mask found - not a problem, probably not set yet
    return models_to_masks


def get(project_name: str, hydrus_model_name: str) -> ShapeMetadata:
    mask = np.load(_get_mask_filename(project_name, hydrus_model_name))
    return ShapeMetadata(mask, project_name, hydrus_model_name)


def save_or_update(mask: ShapeMetadata):
    path = _get_mask_filename(mask.project_name, mask.hydrus_model_name)
    np.save(path, mask.shape_mask)


def delete(project_name: str, hydrus_model_name: str):
    os.remove(_get_mask_filename(project_name, hydrus_model_name))


def _get_mask_filename(project_name: str, hydrus_model_name: str) -> str:
    # workspace/<project>/hydrus/<model>/<model>.npy
    return os.path.join(deployment_config.WORKSPACE_DIR,
                        project_name,
                        "hydrus",
                        hydrus_model_name,
                        hydrus_model_name + MASK_FILETYPE)
