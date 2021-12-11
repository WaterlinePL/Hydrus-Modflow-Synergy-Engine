from kubernetes import client
from kubernetes.client.rest import ApiException

from modflow.modflow_deployer_interface import IModflowDeployer
from utils.yaml_data import YamlData
from utils.yaml_generator import YamlGenerator


class ModflowPodDeployer(IModflowDeployer):

    def __init__(self, api_instance: client.CoreV1Api, path: str, name_file: str,
                 pod_name: str, modflow_version: str = "mf2005", namespace: str = 'default'):
        self.api_instance = api_instance
        self.path = path
        self.pod_name = pod_name
        self.namespace = namespace
        self.name_file = name_file
        self.modflow_version = modflow_version

    def run(self):
        resp = None
        try:
            resp = self.api_instance.read_namespaced_pod(name=self.pod_name, namespace=self.namespace)
        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)

        if not resp:
            yaml_data = YamlData(pod_name=self.pod_name,
                                 container_image='mjstealey/docker-modflow',
                                 container_name='kicajki',
                                 mount_path='/workspace',
                                 mount_path_name='my-path1',
                                 args=[self.modflow_version, self.name_file],
                                 volumes_host_path=self.path)

            yaml_gen = YamlGenerator(yaml_data)
            pod_manifest = yaml_gen.prepare_kubernetes_pod()

            print("Pod %s does not exist. Creating it..." % self.pod_name)
            resp = self.api_instance.create_namespaced_pod(body=pod_manifest, namespace=self.namespace)

        return resp
