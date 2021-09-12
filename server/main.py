# import datapassing.hydrusModflowPassing as dataPasser
# from hydrus.hydrusDeployer import HydrusDeployer
# from modflow.modflowDeployer import ModflowDeployer
# from datapassing.hydrusModflowPassing import HydrusModflowPassing
# from kubernetes import client, config, watch
# from kubernetes.client.rest import ApiException

# def list_all_pods(api: client.CoreV1Api):
#     print("Listing pods with their IPs:")
#     ret = api.list_pod_for_all_namespaces(watch=False)
#     for i in ret.items:
#         print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

from flaskApp import app

if __name__ == '__main__':

    # config.load_kube_config()
    # api_instance = client.CoreV1Api()

    # hydrus_deployer = HydrusDeployer(api_instance=api_instance, pod_name='hydrus-1d')
    # hydrus_pod = hydrus_deployer.run_pod()  # returns V1Pod instance

    # hydrus_modflow_passing = HydrusModflowPassing()
    # hydrus_modflow_passing.update_rch()

    # modflow_deployer = ModflowDeployer(api_instance=api_instance, pod_name='modflow-2005')
    # modflow_v1_pod = modflow_deployer.run_pod()  # returns V1Pod instance

    # # TODO: wait for pods to finish their job and destroy them
    # #  current way to delete pod -> kubectl delete pod modflow-2005
    # watch = watch.Watch()
    # for event in watch.stream(api_instance.list_pod_for_all_namespaces):
    #     o = event['object']
    #     if o.metadata.name in {modflow_v1_pod.metadata.name, hydrus_pod.metadata.name}:
    #         if o.status.container_statuses[0].state.terminated is not None:
    #             terminated = o.status.container_statuses[0].state.terminated
    #             if terminated.reason != 'Completed':
    #                 raise ValueError(o.metadata.name + ' terminated unexpectedly. Reason: ' + terminated.reason)
    #             # print(o.status.container_statuses[0].state.terminated)
    #             # print(o.metadata.name)
    #             else:
    #                 print(o.metadata.name + ' completed successfully. Deleting pod...')
    #                 try:
    #                     api_instance.delete_namespaced_pod(o.metadata.name, o.metadata.namespace)
    #                     break
    #                 except ApiException as ex:
    #                     print(ex)

    # list_all_pods(api=api_instance)
    
    # run flask app
    app.run(debug=True)

