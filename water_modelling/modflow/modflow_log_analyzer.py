from typing import List, Optional, Callable

from app_config import deployment_config
from simulation.simulation_error import SimulationError

# Singleton module
LogLine = str
JoinedLogLines = str  # One string
ErrorDescription = str
FortranJoinedLogLine = str

ModflowErrorCheckFunction = Callable[[JoinedLogLines], ErrorDescription]
FortranErrorCheckFunction = Callable[[FortranJoinedLogLine], ErrorDescription]

LINES_TO_ANALYZE = 15
UNKNOWN_ERROR_LAST_LINES_LOG = 3


def analyze_log(model_name: str, log_lines: List[LogLine]) -> Optional[SimulationError]:
    """
    Analyzes given lines of log in search of errors.
    @param model_name: Name of the Modflow model
    @param log_lines: Lines of Hydrus simulation log to analyze
    @return: Simulation error if such took place
    """

    if deployment_config.LOCAL_DEBUG_MODE:
        whole_log = f"LOG FOR MODFLOW MODEL {model_name}:\n{''.join(log_lines)}"
        print(whole_log)

    joined_log_lines: JoinedLogLines = ''.join(log_lines[-LINES_TO_ANALYZE:])

    modflow_errors: List[ModflowErrorCheckFunction] = [_check_no_file_error,
                                                       _check_missing_nam_file]

    fortran_errors: List[FortranErrorCheckFunction] = [_check_fortran_data_conversion_error,
                                                       _check_fortran_file_read_problem,
                                                       _check_fortran_too_short_list]

    for error_check_function in modflow_errors:
        error = error_check_function(joined_log_lines)
        if error:
            return SimulationError(model_name, error)

    fortran_error_log_line = _retrieve_line_with_fortran_error(log_lines)
    if fortran_error_log_line:
        for error_check_function in fortran_errors:
            error = error_check_function(fortran_error_log_line)
            if error:
                return SimulationError(model_name, error)

    error = _check_for_unknown_error(joined_log_lines, log_lines=log_lines)
    return SimulationError(model_name, error) if error else None


# No file found by Modflow - no .nam file (or wrong path)
def _check_missing_nam_file(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    """
    Modflow error:
        Can't find name file simple1.nam or simple1.nam.nam

    1. Split on 'Can't find name file ' - take second element with filenames
    2. Split on ' or ' and trim both elements
    """
    error_msg_content = "Can't find name file "
    if error_msg_content in log_to_analyze:
        missing_files = log_to_analyze.split(error_msg_content)[1].split(' or ')
        return f"Missing file - cannot locate file {missing_files[0].strip()} nor {missing_files[1].strip()}. " \
               f"Make sure it is located in the provided .zip."
    return None


# Remove input file from project (ex. remove .dis file)
def _check_no_file_error(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    """
    Sample log:
        *** ERROR OPENING FILE "simple1.dis" ON UNIT    12
           SPECIFIED FILE STATUS: OLD
           SPECIFIED FILE FORMAT: FORMATTED
           SPECIFIED FILE ACCESS: SEQUENTIAL
           SPECIFIED FILE ACTION: READ
      -- STOP EXECUTION (SGWF2BAS7OPEN)

    When creating not_found_file variable:
    1. Split on 'ERROR OPENING FILE ' and take second part ('"simple1.dis" ON UNIT ...')
    2. Split on " - get 3 elements in list (since there are 2 places were we split) and take middle element - filename
    """
    error_msg_content = "ERROR OPENING FILE "
    if error_msg_content in log_to_analyze:
        not_found_file = log_to_analyze.split(error_msg_content)[1].split('"')[1]
        return f"Problem occurred while opening file {not_found_file} - make sure it was provided inside the .zip " \
               f"file containing Modflow model. "
    return None


# List longer than provided values - delete any value (without CONSTANT prefix) in .lpf
def _check_fortran_too_short_list(fortran_log_line: FortranJoinedLogLine) -> Optional[ErrorDescription]:
    """
    Docker fortran error:
        At line 169 of file gwf2lpf7.f (unit = 14, file = 'simple1.lpf')
        Fortran runtime error: Bad integer for item 1 in list input

    Desktop fortran error:
        forrtl: severe (59): list-directed I/O syntax error, unit 14, file <path>\modflow\simple1\simple1.lpf
    """
    desktop_error_msg_content = "list-directed I/O syntax error"
    docker_error_msg_content = "Fortran runtime error: Bad integer for item 1 in list input"
    related_file = _return_file_if_error_occurred(fortran_log_line,
                                                  desktop_err_msg=desktop_error_msg_content,
                                                  docker_err_msg=docker_error_msg_content)
    if related_file:
        return f"Error while reading file {related_file} - problem occurred on creating a list of values. It may be " \
               f"too short."
    return None


# Attempt to convert wrong data type - delete entire 2D array of any stress period but leave labels in .rch
def _check_fortran_data_conversion_error(fortran_log_line: FortranJoinedLogLine) -> Optional[ErrorDescription]:
    """
    Docker fortran error:
        At line 881 of file utl7.f (unit = 24, file = 'simple1.rch')
        Fortran runtime error: Bad value during floating point read

    Desktop fortran error:
        forrtl: severe (64): input conversion error, unit 24, file <path>\modflow\simple1\simple1.rch
        + stacktrace
    """
    desktop_error_msg_content = "input conversion error"
    docker_error_msg_content = "Fortran runtime error: Bad value during floating point read"
    related_file = _return_file_if_error_occurred(fortran_log_line,
                                                  desktop_err_msg=desktop_error_msg_content,
                                                  docker_err_msg=docker_error_msg_content)
    if related_file:
        return f"Error while reading file {related_file} - conversion to float value failed."
    return None


# Cut content from any input file (ex. delete any constant from .lpf or .dis)
def _check_fortran_file_read_problem(fortran_log_line: FortranJoinedLogLine):
    """
    Docker image fortran error:
        At line 772 of file gwf2bas7.f (unit = 12, file = 'simple1.dis')
        Fortran runtime error: End of file

    Desktop fortran error:
        forrtl: severe (24): end-of-file during read, unit 14, file <path>\modflow\simple1\simple1.lpf
         + stacktrace
    """
    desktop_error_msg_content = "end-of-file during read"
    docker_error_msg_content = "Fortran runtime error: End of file"
    related_file = _return_file_if_error_occurred(fortran_log_line,
                                                  desktop_err_msg=desktop_error_msg_content,
                                                  docker_err_msg=docker_error_msg_content)
    if related_file:
        return f"Error while reading file {related_file} - please check for missing input data in this file."
    return None


def _check_for_unknown_error(log_to_analyze: JoinedLogLines, log_lines: List[LogLine]) -> Optional[ErrorDescription]:
    successful_simulation_msg = "Normal termination of simulation"
    if successful_simulation_msg in log_to_analyze:
        return None

    clean_log_lines = log_lines_without_stacktrace(log_lines)
    unknown_error_log_line_count = min(UNKNOWN_ERROR_LAST_LINES_LOG, len(clean_log_lines))
    return f"Unknown error, last log lines: {'<br/>'.join(clean_log_lines[-unknown_error_log_line_count:])}"


# Utility functions
def _retrieve_line_with_fortran_error(log_lines: List[LogLine]) -> Optional[LogLine]:
    fortran_desktop_keyword = "forrtl"
    fortran_image_keywords = "Fortran runtime error"
    for i, line in enumerate(log_lines):
        if fortran_desktop_keyword in line:
            return line
        if fortran_image_keywords in line:
            return ' '.join([log_lines[i - 1], log_lines[i]])
    return None


def _extract_file_from_fortran_error(fortran_log_line: LogLine, desktop_case: bool) -> str:
    """
    Docker image fortran error:
        At line 772 of file gwf2bas7.f (unit = 12, file = 'simple1.dis')
        Fortran runtime error: End of file

    In Docker case:
    1. split on 'file = ' and take second part - begins with the filename
    2. Split on ' - get 3 elements in list (since there are 2 places were we split) and take middle element - filename

    Desktop fortran error:
    forrtl: severe (24): end-of-file during read, unit 14, file <path>\modflow\simple1\simple1.lpf
     + stacktrace

    In desktop case: Split on folder-separator ('\' for Windows, '/' for Linux) and take trimmed last element
    """
    if desktop_case:
        linux_split = fortran_log_line.split('/')
        if len(linux_split) > 1 and check_linux_path_case(linux_split):  # Linux path (just in case)
            return linux_split[-1].strip()
        else:  # Windows path
            windows_split = fortran_log_line.split('\\')
            return windows_split[-1].strip()
    else:
        return fortran_log_line.split("file = ")[1].split('\'')[1]


def _return_file_if_error_occurred(fortran_log_line: LogLine,
                                   desktop_err_msg: str,
                                   docker_err_msg: str) -> Optional[str]:
    if desktop_err_msg in fortran_log_line:
        return _extract_file_from_fortran_error(fortran_log_line, desktop_case=True)
    elif docker_err_msg in fortran_log_line:
        return _extract_file_from_fortran_error(fortran_log_line, desktop_case=False)
    return None


def log_lines_without_stacktrace(log_lines: List[LogLine]) -> List[LogLine]:
    for i, line in enumerate(log_lines):
        if line.startswith("Image"):
            return log_lines[:i]
    return log_lines


def check_linux_path_case(linux_split: List[str]) -> bool:
    for split_element in linux_split:
        if split_element.endswith("file "):
            return True
    return False
