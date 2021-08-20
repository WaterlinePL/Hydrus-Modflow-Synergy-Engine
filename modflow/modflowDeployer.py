from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
from os import path
from constants import MODFLOW_ROOT_DOCKER
from utils.yaml_data import YamlData
from utils.yaml_generator import YamlGenerator

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
    yaml_data = YamlData(pod_name='modflow-2005',
                         container_image='mjstealey/docker-modflow',
                         container_name='kicajki',
                         mount_path='/workspace',
                         mount_path_name='my-path',
                         args=["mf2005", "simple1.nam"],
                         volumes_host_path=MODFLOW_ROOT_DOCKER)

    yaml_gen = YamlGenerator(yaml_data)
    pod_manifest = yaml_gen.prepare_kubernetes_pod()

    print("Pod %s does not exist. Creating it..." % yaml_data.pod_name)
    resp = api_instance.create_namespaced_pod(body=pod_manifest,
                                              namespace='default')


print("Listing pods with their IPs:")
ret = api_instance.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

