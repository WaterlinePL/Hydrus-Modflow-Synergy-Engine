import os

from deployment import daos
from metadata.project_metadata import ProjectMetadata
from modflow import modflow_utils
from server.user_state import UserState


def load_metadata_to_state(state: UserState, chosen_project: ProjectMetadata) -> None:
    # clear old data and load new project
    state.reset_project_data()
    state.loaded_project = chosen_project

    _try_load_modflow_data(state)
    _try_load_hydrus_masks(state, chosen_project)


def _try_load_modflow_data(state: UserState):
    if state.loaded_project.modflow_model:
        model_path = os.path.join(state.get_modflow_dir(), state.loaded_project.modflow_model)
        nam_file_name = modflow_utils.get_nam_file(model_path)
        model_data = modflow_utils.get_model_data(model_path, nam_file_name)
        state.recharge_masks = modflow_utils.get_shapes_from_rch(
            model_path, nam_file_name, (model_data["rows"], model_data["cols"])
        )


def _try_load_hydrus_masks(state: UserState, project_metadata: ProjectMetadata):
    if state.loaded_project.hydrus_models:
        state.loaded_shapes = daos.mask_dao.scan_for_mask_in_project(project_metadata.name)
