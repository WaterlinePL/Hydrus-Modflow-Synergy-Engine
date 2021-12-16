from time import sleep

from kubernetes import client, watch
from kubernetes.client.rest import ApiException

from deployment.kubernetes_job_interface import IKubernetesJob
from utils.yaml_generator import YamlGenerator


class JobController:
    MAX_RETRIES = 3
    MAX_FAILED_JOBS = YamlGenerator.BACKOFF_LIMIT + 1

    @staticmethod
    def wait_for_job_termination(job: IKubernetesJob) -> None:
        retry_count = JobController.MAX_RETRIES
        job_status = job.get_job_status()

        while not job_status and retry_count > 0:
            sleep(2)
            job_status = job.get_job_status()
            retry_count -= 1

        if not job_status:
            raise SystemExit("Job was not added to k8s cluster. Internal fatal error!")

        # FIXME: jeśli pod joba nie wystartuje (np. przez brak PVC) to job jest zawsze active
        while job_status.active:
            sleep(2)
            job_status = job.get_job_status()

            if job_status.succeeded == 1:
                return
            if job_status.failed == JobController.MAX_FAILED_JOBS:
                raise SystemError("Job failed too many times!")
            if not job_status.active:
                raise SystemError("Job is inactibe for unknown reasons - debug inside cluster.")

    # DEPRECATED
    def wait_for_pod_termination(self, job_name: str) -> None:
        """
        @param job: Job to monitor. Job's name must be unique (ex. "hydrus-1d-01")
        @return: None
        """
        pod_watch = watch.Watch()
        for event in pod_watch.stream(self.api_instance.list_pod_for_all_namespaces, watch=True):
            event_object = event['object']
            if event_object.metadata.name == job_name:
                if self.is_completed(event_object.status):
                    if self.delete_pod(event_object.metadata.namespace, job_name):
                        pod_watch.stop()

    # DEPRECATED - we do not want to delete pods/jobs
    def delete_pod(self, namespace: str, pod_name: str) -> bool:
        """
        @param namespace: Namespace of the pod you want to delete (ex. "default")
        @param pod_name: Name of the pod you want to delete (ex. "hydrus-1d-01")
        @return: None
        """
        print('Deleting pod ' + pod_name)
        try:
            self.api_instance.delete_namespaced_pod(pod_name, namespace)
            print('Pod deleted successfully')
            return True
        except ApiException as ex:
            print('Could not delete pod ' + pod_name + '.\n' + ex)
            return False

    # DEPRECATED
    @staticmethod
    def is_completed(pod_status) -> bool:
        """
        @param pod_status: Status of watch event object (event['object'].status)
        @return: True if pod completed successfully. False if the pod is still running.
        Raises exception on unexpected pod termination.
        """
        if pod_status.container_statuses is None or \
                pod_status.container_statuses[0].state.terminated is None:
            return False

        if pod_status.container_statuses[0].state.terminated.reason == 'Completed':
            return True

        raise Exception('Pod terminated unexpectedly. Reason: ' +
                        pod_status.container_statuses[0].state.terminated.reason)
