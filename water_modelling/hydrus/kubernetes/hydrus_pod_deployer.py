from kubernetes.client.rest import ApiException

from deployment.kubernetes_deployer import KubernetesDeployer
from hydrus.hydrus_deployer_interface import IHydrusDeployer
from utils.yaml_data import YamlData
from utils.yaml_generator import YamlGenerator


class _HydrusPodDeployer(IHydrusDeployer):

    def __init__(self, kubernetes_deployer: KubernetesDeployer, sub_path: str, job_name: str, namespace: str = 'default'):
        self.kubernetes_deployer = kubernetes_deployer
        self.path = sub_path
        self.job_name = job_name
        self.namespace = namespace

    def run(self):
        resp = None
        try:
            resp = self._get_k8s_client().read_namespaced_pod(name=self.job_name, namespace=self.namespace)

        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)

        if not resp:
            yaml_data = YamlData(job_name=self.job_name,
                                 container_image='observer46/water_modeling_agh:hydrus1d_linux',
                                 container_name='kicajki2',
                                 mount_path='/workspace/hydrus',
                                 args=[],
                                 volumes_host_path=self.path)

            yaml_gen = YamlGenerator(yaml_data)
            pod_manifest = yaml_gen.prepare_kubernetes_job()

            print("Job %s does not exist. Creating it..." % self.job_name)
            resp = self._get_k8s_client().create_namespaced_pod(body=pod_manifest, namespace=self.namespace)

        return resp

    def _get_k8s_client(self):
        return self.kubernetes_deployer.api_instance
