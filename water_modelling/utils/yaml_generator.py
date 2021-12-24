import os

from utils.yaml_data import YamlData


class YamlGenerator:

    VOLUME_NAME = "project-volume"
    PVC_NAME = os.environ['PVC']
    BACKOFF_LIMIT = 2

    def __init__(self, data: YamlData):
        self.data = data

    def prepare_kubernetes_job(self):
        containers = [{
            'image': self.data.container_image,
            'name': self.data.container_name,
            'volumeMounts': [{
                'mountPath': self.data.mount_path,
                'name': YamlGenerator.VOLUME_NAME,
                'subPath': self.data.sub_path
            }],
            'args': self.data.args
        }]

        volumes = [{
            'name': YamlGenerator.VOLUME_NAME,
            'persistentVolumeClaim': {
                'claimName': YamlGenerator.PVC_NAME
            }
        }]

        spec = {
            'containers': containers,
            'volumes': volumes,
            'restartPolicy': 'Never'
        }

        config = {
            'apiVersion': 'batch/v1',
            'kind': 'Job',
            'metadata': {
                'name': self.data.job_name,
                'annotations': {
                    'programme': self.data.hydro_programme,
                    'description': self.data.description
                }
            },
            'spec': {
                'template': {
                    'spec': spec
                },
                'backoffLimit': YamlGenerator.BACKOFF_LIMIT
            }
        }

        return config
