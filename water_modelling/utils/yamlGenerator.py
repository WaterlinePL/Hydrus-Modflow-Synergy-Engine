from utils.yamlData import YamlData


class YamlGenerator:

    def __init__(self, data: YamlData):
        self.data = data

    def prepare_kubernetes_pod(self):
        containers = [{
            'image': self.data.container_image,
            'name': self.data.container_name,
            'volumeMounts': [{
                'mountPath': self.data.mount_path,
                'name': self.data.mount_path_name
            }],
            'args': self.data.args,
            'securityContext': {'privileged': True}
        }]

        volumes = [{
            'name': self.data.mount_path_name,
            'hostPath': {
                'path': self.data.volumes_host_path,
                'type': 'DirectoryOrCreate'
            }
        }]

        spec = {
            'containers': containers,
            'volumes': volumes,
            'restartPolicy': 'Never'
        }

        config = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': self.data.pod_name
            },
            'spec': spec
        }

        return config
