from time import sleep
from typing import Optional, List, Tuple

from deployment.kubernetes_job_interface import IKubernetesJob
from simulation.simulation_error import SimulationError
from utils.yaml_generator import YamlGenerator

LOG_LINE = str
MODEL_NAME = str


class JobController:
    INITIALIZATION_MAX_RETRIES = 3
    MAX_FAILED_JOBS = YamlGenerator.BACKOFF_LIMIT + 1
    LATEST_POD_STATUS_CHECK_FREQUENCY = 5

    @staticmethod
    def wait_for_job_termination(job_deployer: IKubernetesJob) -> Tuple[MODEL_NAME, List[LOG_LINE]]:
        initialization_retry_count = JobController.INITIALIZATION_MAX_RETRIES
        job_status = job_deployer.get_job_status()

        while not job_status and initialization_retry_count > 0:
            sleep(2)
            job_status = job_deployer.get_job_status()
            initialization_retry_count -= 1

        attempts_to_check_pod = JobController.LATEST_POD_STATUS_CHECK_FREQUENCY
        if not job_status:
            # Should not happen, possibly wrong mapping between created job and watched job
            return (job_deployer.get_model_name(),
                    [f"Job was not added to kubernetes cluster or job's name mismatch. Internal fatal error!"])

        while True:
            sleep(2)
            attempts_to_check_pod -= 1
            job_status = job_deployer.get_job_status()

            if job_status.succeeded == 1 or job_status.failed == JobController.MAX_FAILED_JOBS:
                # Success or simulation error
                break

            if not job_status.active:
                # Job not active for unknown reasons
                return (job_deployer.get_model_name(),
                        [f"Job is inactive for unknown reasons. Check it's status using "
                         f"'kubectl describe job {job_deployer.job_name}' in terminal."])

            if attempts_to_check_pod < 0 and job_status.active:
                # Job's pod did not start, ex. due to not existing PVC
                attempts_to_check_pod = JobController.LATEST_POD_STATUS_CHECK_FREQUENCY
                latest_pod = job_deployer.get_latest_pod()

                if latest_pod.status.phase == "Pending":
                    return (job_deployer.get_model_name(),
                            [f"Pod has pending status. Check status of pod using "
                             f"'kubectl describe pod {latest_pod.metadata.name}' in terminal. Possibly incorrect PVC."])

        return job_deployer.get_model_name(), job_deployer.get_latest_logs().split('\n')
