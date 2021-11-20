import os
from typing import List

EXPECTED_INPUT_FILES = ["SELECTOR.IN", "ATMOSPH.IN"]


def get_hydrus_input_files(project_path: str) -> List[str]:
    return [file.lower() for file in os.listdir(project_path) if file.lower().endswith(".in")]


def validate_model(project_path: str):
    input_files = get_hydrus_input_files(project_path)
    for expected_file in EXPECTED_INPUT_FILES:
        if expected_file.lower() not in input_files:
            return False
    return True
