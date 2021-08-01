from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml
from os import path


def deployHydrus():
    config.load_kube_config()
    api_instance = client.CoreV1Api()

    name = 'hydrus-1d'
    resp = None
    try:
        resp = api_instance.read_namespaced_pod(name=name, namespace='default')
    except ApiException as e:
        if e.status != 404:
            print("Unknown error: %s" % e)
            exit(1)

    if not resp:
        print("Pod %s does not exist. Creating it..." % name)
        with open(path.join(path.dirname(__file__), "config.yaml")) as f:
            pod_manifest = yaml.safe_load(f)

        resp = api_instance.create_namespaced_pod(body=pod_manifest, namespace='default')

    print("Listing pods with their IPs:")
    ret = api_instance.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

