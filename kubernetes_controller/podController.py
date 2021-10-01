from kubernetes import client, watch
from kubernetes.client.rest import ApiException


class PodController:

    def __init__(self, api_instance: client.CoreV1Api):
        self.api_instance = api_instance

    def wait_for_pod_termination(self, pod_name: str) -> None:
        """
        @param pod_name: Name of the pod you want to terminate. Must be unique (ex. "hydrus-1d-01")
        @return: None
        """
        pod_watch = watch.Watch()
        for event in pod_watch.stream(self.api_instance.list_pod_for_all_namespaces, watch=True):
            event_object = event['object']
            if event_object.metadata.name == pod_name:
                if self.is_completed(event_object.status):
                    if self.delete_pod(event_object.metadata.namespace, pod_name):
                        pod_watch.stop()

    def delete_pod(self, namespace: str, pod_name: str) -> None:
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

    def is_completed(self, pod_status) -> bool:
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
