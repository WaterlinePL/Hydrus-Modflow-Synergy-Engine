
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
from os import path

config.load_kube_config()
api_instance = client.CoreV1Api()


name = 'modflow-2005'
resp = None
try:
    resp = api_instance.read_namespaced_pod(name=name,
                                            namespace='default')
except ApiException as e:
    if e.status != 404:
        print("Unknown error: %s" % e)
        exit(1)

if not resp:
    print("Pod %s does not exist. Creating it..." % name)
    with open(path.join(path.dirname(__file__), "config.yaml")) as f:
        pod_manifest = yaml.safe_load(f)
    #     {
    #     'apiVersion': 'v1',
    #     'kind': 'Pod',
    #     'metadata': {
    #         'name': name
    #     },
    #     'spec': {
    #         'containers': [{
    #             'image': 'mjstealey/docker-modflow',
    #             'name': 'kicajki',
    #             'volumeMounts': [{
    #                 'mountPath': '/workspace',
    #                 'name': 'my-path'
    #             }],
    #             "args": [
    #                 "mf2005",
    #                 "tutorial_2.nam"
    #             ]
    #         }],
    #         'volumes': [{
    #             'name': 'my-path',
    #             'hostPath': {
    #                 'path': 'C:/Users/Admin/Documents/Studia/Praca_inzynierska/studnia_docker_files'
    #             }
    #         }]
    #     }
    # }
    resp = api_instance.create_namespaced_pod(body=pod_manifest,
                                              namespace='default')


print("Listing pods with their IPs:")
ret = api_instance.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))





