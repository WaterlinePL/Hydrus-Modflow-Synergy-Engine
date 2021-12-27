from typing import List, Optional, Callable

from app_config import deployment_config
from simulation.simulation_error import SimulationError

# Singleton module
LogLine = str
JoinedLogLines = str  # One string
ErrorDescription = str
ErrorCheckFunction = Callable[[JoinedLogLines], ErrorDescription]

LINES_TO_ANALYZE = 10
UNKNOWN_ERROR_LAST_LINES_LOG = 3


def analyze_log(model_name: str, log_lines: List[LogLine]) -> Optional[SimulationError]:
    """
    Analyzes given lines of log in search of errors.
    @param model_name: Name of the Hydrus model
    @param log_lines: Lines of Hydrus simulation log to analyze
    @return: Simulation error if such took place
    """

    if deployment_config.LOCAL_DEBUG_MODE:
        whole_log = f"LOG FOR HYDRUS MODEL {model_name}:\n{''.join(log_lines)}"
        print(whole_log)

    joined_log_lines: JoinedLogLines = ''.join(log_lines[-LINES_TO_ANALYZE:])

    basic_error_checks: List[ErrorCheckFunction] = [_check_no_folder_error,
                                                    _check_convergence_error,
                                                    _check_initial_time_step_error,
                                                    _check_basic_info_error]

    for error_check_function in basic_error_checks:
        error = error_check_function(joined_log_lines)
        if error:
            return SimulationError(model_name, error)

    error = _check_no_file_error(joined_log_lines, model_name=model_name)
    if error:
        return SimulationError(model_name, error)

    error = _check_for_unknown_error(joined_log_lines, log_lines=log_lines)
    return SimulationError(model_name, error) if error else None


# Wrong path
def _check_no_folder_error(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    error_msg_content = "Folder with input data of the specified project does not exist"
    if error_msg_content in log_to_analyze:
        return "Problem with path to project - project might not exist or path may be too long or incorrect." \
               "Please, avoid uppercase letters and special symbols (except from '-' and '.') in the name of the model."
    return None


# Missing input file (ex. ATMOSPH.IN)
def _check_no_file_error(log_to_analyze: JoinedLogLines, model_name: str) -> Optional[ErrorDescription]:
    error_msg_content = "Open file error in file"
    if error_msg_content in log_to_analyze:
        not_found_file = log_to_analyze.split(f"{model_name}")[1].split('\n')[0][1:]
        return f"Problem occurred while opening file {not_found_file} - make sure it was provided inside the .zip " \
               f"file containing Hydrus model. "
    return None


# Delete values in one row of ATMOSPH.IN but leave number at the beginning of the row (tAtm)
def _check_convergence_error(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    error_msg_numerical_content = "Numerical solution"
    error_msg_convergence_content = "not converged"
    if error_msg_numerical_content in log_to_analyze and error_msg_convergence_content in log_to_analyze:
        return "Numerical solution cannot converge - check if input data is correct."
    return None


# Delete every row in ATMOSPH.IN but leave column names and last line (empty input)
def _check_initial_time_step_error(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    error_msg_content = "The first time-variable BC record is at time smaller than tInit+dtInit"
    if error_msg_content in log_to_analyze:
        return "Too big initial time step - consider lowering it. This error may occur as well if ATMOSPH.IN is empty."
    return None


# Delete line under 'Wat   lChem lTemp' in Selector.in
def _check_basic_info_error(log_to_analyze: JoinedLogLines) -> Optional[ErrorDescription]:
    error_msg_content = "Error when reading from an input file Selector.in BasicInformations"
    if error_msg_content in log_to_analyze:
        return "An error occurred while reading basic model information from file Selector.in. " \
               "Please check correctness of data stored in this file."
    return None


# Check if simulation ended successfully, if not return unknown error
def _check_for_unknown_error(log_to_analyze: JoinedLogLines, log_lines: List[LogLine]) -> Optional[ErrorDescription]:
    successful_simulation_docker = "Calculation complete"
    successful_simulation_local = "successfully"
    time_word = "time"

    if time_word in log_to_analyze and \
            (successful_simulation_docker in log_to_analyze or successful_simulation_local in log_to_analyze):
        return None

    log_without_backtrace = create_log_without_backtrace(log_lines)
    unknown_error_log_line_count = min(UNKNOWN_ERROR_LAST_LINES_LOG, len(log_without_backtrace))
    return f"Unknown error, last log lines: {'<br>'.join(log_without_backtrace[-unknown_error_log_line_count:])}"


def create_log_without_backtrace(log_lines: List[LogLine]) -> List[LogLine]:
    fortran_message_before_backtrace = "Fortran runtime error"
    for i, line in enumerate(log_lines):
        if line.startswith(fortran_message_before_backtrace):
            return log_lines[:i + 1]        # inclusive
    return log_lines
