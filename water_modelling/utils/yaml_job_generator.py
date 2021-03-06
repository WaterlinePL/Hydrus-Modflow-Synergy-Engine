import os

from utils.yaml_data import YamlData


class YamlJobGenerator:
    # IMPORTANT: create env variable 'PVC' with name of PVC
    # (default from .yaml: 'nfs-pvc')
    PVC_NAME = os.environ['PVC']
    VOLUME_NAME = "project-volume"
    BACKOFF_LIMIT = 2

    def __init__(self, data: YamlData):
        self.data = data

    def prepare_kubernetes_job(self):
        containers = [{
            'image': self.data.container_image,
            'name': self.data.container_name,
            'volumeMounts': [{
                'mountPath': self.data.mount_path,
                'name': YamlJobGenerator.VOLUME_NAME,
                'subPath': self.data.sub_path
            }],
            'args': self.data.args
        }]

        volumes = [{
            'name': YamlJobGenerator.VOLUME_NAME,
            'persistentVolumeClaim': {
                'claimName': YamlJobGenerator.PVC_NAME
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
                    'program': self.data.hydro_program,
                    'description': self.data.description
                }
            },
            'spec': {
                'template': {
                    'spec': spec
                },
                'backoffLimit': YamlJobGenerator.BACKOFF_LIMIT
            }
        }

        return config
