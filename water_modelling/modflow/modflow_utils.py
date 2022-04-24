from typing import Tuple, Optional, List

import flopy
import os

import numpy as np
from collections import deque


def get_model_data(project_path: str, nam_file_name: str) -> dict:
    """
    Get the following info about the modflow model:
    {
        "rows": the amount of rows in the model,
        "cols": the amount of columns in the model,
        "grid_unit": the unit in which the cell dimensions are given,
        "row_cells": the height of each row,
        "col_cells": the width of each column
    }

    @param project_path: Path to Modflow project main directory
    @param nam_file_name: Name of .nam file inside the Modflow project
    @return: A dictionary of info as described above.
    """

    modflow_model = flopy.modflow.Modflow \
        .load(nam_file_name, model_ws=project_path, load_only=["rch", "dis"], forgive=True)
    return {
        "rows": modflow_model.nrow,
        "cols": modflow_model.ncol,
        "row_cells": modflow_model.dis.delc.array.tolist(),
        "col_cells": modflow_model.dis.delr.array.tolist(),
        "grid_unit": modflow_model.modelgrid.units
    }


def scale_cells_size(row_cells: List[float], col_cells: List[float], max_width) -> Tuple[List[int], List[int]]:
    """
    Get cells size of modflow model
    @param col_cells: list of modflow model cols width
    @param row_cells: list of modflow model rows height
    @param max_width: Parameter for scaling purposes
    @return: Tuple with lists containing width of the Modflow project cells (row_cells, col_cells)
    """

    sum_width = sum(col_cells)
    sum_height = sum(row_cells)

    width = max_width
    height = max_width * (sum_height / sum_width)

    scale_x = sum_width / width
    scale_y = sum_height / height

    row_cells = np.divide(row_cells, scale_x)
    col_cells = np.divide(col_cells, scale_y)

    return row_cells, col_cells


def validate_model(project_path: str, nam_file_name: str) -> bool:
    """
    Validates modflow model - check if it contains .nam file (list of files), .rch file (recharge),
    perform recharge check.

    @param project_path: Path to Modflow project main directory
    @param nam_file_name: Name of .nam file inside the Modflow project
    @return: True if model is valid, False otherwise
    """

    if not nam_file_name:
        return False

    try:
        # load whole model and validate it
        m = flopy.modflow.Modflow.load(nam_file_name, model_ws=project_path, forgive=True, check=True)
        if m.rch is None:
            print("Model doesn't contain .rch file")
            return False
        m.rch.check()
    except IOError:
        print("Model is not valid - files are missing")
        return False
    except KeyError:
        print("Model is not valid - modflow common error")
        return False

    return True


def get_shapes_from_rch(project_path: str, nam_file_name: str, project_shape: Tuple[int, int]) -> List[np.ndarray]:
    """
    Defines shapes masks for uploaded Modflow model based on recharge

    @param project_path: Path to Modflow project main directory
    @param nam_file_name: Name of .nam file inside the Modflow project
    @param project_shape: Tuple representing size of the Modflow project (rows, cols)
    @return: List of shapes read from Modflow project
    """

    modflow_model = flopy.modflow.Modflow \
        .load(nam_file_name, model_ws=project_path, load_only=["rch"], forgive=True)

    stress_period = 0
    layer = 0

    recharge_masks = []
    is_checked_array = np.full(project_shape, False)
    recharge_array = modflow_model.rch.rech.array[stress_period][layer]
    modflow_rows, modflow_cols = project_shape

    for row in range(modflow_rows):
        for col in range(modflow_cols):
            if not is_checked_array[row][col]:
                recharge_masks.append(np.zeros(project_shape))
                _fill_mask_iterative(mask=recharge_masks[-1], recharge_array=recharge_array,
                                     is_checked_array=is_checked_array,
                                     project_shape=project_shape,
                                     row=row, col=col,
                                     value=recharge_array[row][col])

    return recharge_masks


def get_nam_file(project_path: str) -> Optional[str]:
    for filename in os.listdir(project_path):
        filename = str(filename)
        if filename.endswith(".nam"):
            return filename

    print("ERROR: invalid modflow model; missing .nam file")
    return None


def _fill_mask_iterative(mask: np.ndarray, recharge_array: np.ndarray, is_checked_array: np.ndarray,
                         project_shape: Tuple[int, int], row: int, col: int, value: float):
    """
    Fill given mask with 1's according to recharge array (using DFS)

    @param mask: Binary mask of current shape - initially filled with 0's
    @param recharge_array: 2d array filled with modflow model recharge values
    @param is_checked_array: Control array - 'True' means that given cell was already used in one of the masks
    @param project_shape: Tuple representing shape of the Modflow project (rows, cols)
    @param row: Current column index
    @param col: Current row index
    @param value: Recharge value of current mask
    @return: None (result inside variable @mask)
    """
    modflow_rows, modflow_cols = project_shape

    stack = deque()
    stack.append((row, col))

    while stack:
        cur_row, cur_col = stack.pop()
        # return condition - out of bounds or given cell was already used
        if cur_row < 0 or cur_row >= modflow_rows or cur_col < 0 or cur_col >= modflow_cols or \
                is_checked_array[cur_row][cur_col]:
            continue

        if recharge_array[cur_row][cur_col] == value:
            is_checked_array[cur_row][cur_col] = True
            mask[cur_row][cur_col] = 1
            stack.append((cur_row - 1, cur_col))
            stack.append((cur_row + 1, cur_col))
            stack.append((cur_row, cur_col - 1))
            stack.append((cur_row, cur_col + 1))

    return
