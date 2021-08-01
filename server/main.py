import datapassing.hydrusModflowPassing as dataPasser
from hydrus.hydrusDeployer import deployHydrus
from modflow.modflowDeployer import deployModflow
from kubernetes import client, config, watch

if __name__ == '__main__':
    

    api_instance = client.CoreV1Api()
    count = 10
    watch = watch.Watch()
    for event in watch.stream(api_instance.list_namespace, _request_timeout=60):
        print("Event: %s %s" % (event['type'], event['object'].metadata.name))
        print(client.V1PodStatus().container_statuses)
        count -= 1
        if not count:
            watch.stop()

    deployHydrus()
    dataPasser.updateRch()
    deployModflow()


