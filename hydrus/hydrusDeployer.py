from kubernetes import client
from kubernetes.client.rest import ApiException
from utils.yamlData import YamlData
from utils.yamlGenerator import YamlGenerator
from constants import HYDRUS_ROOT_DOCKER


class HydrusDeployer:

    def __init__(self, api_instance: client.CoreV1Api, pod_name, namespace='default'):
        self.api_instance = api_instance
        self.pod_name = pod_name
        self.namespace = namespace

    def run_pod(self):
        resp = None
        try:
            resp = self.api_instance.read_namespaced_pod(name=self.pod_name, namespace=self.namespace)

        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)

        if not resp:
            yaml_data = YamlData(pod_name=self.pod_name,
                                 container_image='observer46/water_modeling_agh:hydrus1d_linux',
                                 container_name='kicajki2',
                                 mount_path='/workspace/hydrus',
                                 mount_path_name='my-path2',
                                 args=[],
                                 volumes_host_path=HYDRUS_ROOT_DOCKER)

            yaml_gen = YamlGenerator(yaml_data)
            pod_manifest = yaml_gen.prepare_kubernetes_pod()

            print("Pod %s does not exist. Creating it..." % self.pod_name)
            resp = self.api_instance.create_namespaced_pod(body=pod_manifest, namespace=self.namespace)

        return resp
