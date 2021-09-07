# import datapassing.hydrusModflowPassing as dataPasser
# from hydrus.hydrusDeployer import HydrusDeployer
# from modflow.modflowDeployer import ModflowDeployer
# from datapassing.hydrusModflowPassing import HydrusModflowPassing
from kubernetes import client, config, watch

from flaskApp import app


def list_all_pods(api: client.CoreV1Api):
    print("Listing pods with their IPs:")
    ret = api.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


if __name__ == '__main__':

    # run flask app
    app.run(debug=True)

    # # manage kubernetes
    # config.load_kube_config()
    # api_instance = client.CoreV1Api()
    #
    # # count = 10
    # # watch = watch.Watch()
    # # for event in watch.stream(api_instance.list_namespace, _request_timeout=60):
    # #     print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    # #     print(client.V1PodStatus().container_statuses)
    # #     count -= 1
    # #     if not count:
    # #         watch.stop()
    #
    # hydrus_deployer = HydrusDeployer(api_instance=api_instance, pod_name='hydrus-1d')
    # hydrus_pod = hydrus_deployer.run_pod()          # returns V1Pod instance
    #
    # hydrus_modflow_passing = HydrusModflowPassing()
    # hydrus_modflow_passing.update_rch()
    #
    # modflow_deployer = ModflowDeployer(api_instance=api_instance, pod_name='modflow-2005')
    # modflow_v1_pod = modflow_deployer.run_pod()      # returns V1Pod instance
    #
    # # TODO: wait for pods to finish their job and destroy them
    # #  current way to delete pod -> kubectl delete pod modflow-2005
    #
    # list_all_pods(api=api_instance)
