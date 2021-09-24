from kubernetes import client, watch
from kubernetes.client.rest import ApiException


class PodController:

    def __init__(self, api_instance: client.CoreV1Api):
        self.api_instance = api_instance

    def wait_for_pod_termination(self, pod_name: str) -> None:
        pod_watch = watch.Watch()
        for event in pod_watch.stream(self.api_instance.list_pod_for_all_namespaces, watch=True):
            o = event['object']
            if o.metadata.name == pod_name:
                if self.is_completed(o.status):
                    self.delete_pod(o.metadata.namespace, pod_name)
                    pod_watch.stop()

    def delete_pod(self, namespace: str, pod_name: str) -> None:
        print('Deleting pod ' + pod_name)
        try:
            self.api_instance.delete_namespaced_pod(pod_name, namespace)
            print('Pod deleted successfully')
        except ApiException as ex:
            print('Could not delete pod ' + pod_name + '.\n' + ex)

    def is_completed(self, pod_status) -> bool:
        if pod_status.container_statuses is None or \
                pod_status.container_statuses[0].state.terminated is None:
            return False

        if pod_status.container_statuses[0].state.terminated.reason == 'Completed':
            return True

        raise Exception('Pod terminated unexpectedly. Reason: ' +
                        pod_status.container_statuses[0].state.terminated.reason)
