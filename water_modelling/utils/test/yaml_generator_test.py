import unittest
import yaml

from utils.yaml_data import YamlData
from utils.yaml_job_generator import YamlJobGenerator


class YamlGeneratorTest(unittest.TestCase):

    def test_should_create_yaml(self):
        # given
        YamlJobGenerator.PVC_NAME = "nfs-pvc"
        yaml_data = YamlData(job_name="job_name",
                             container_image="container_image",
                             container_name="container_name",
                             mount_path="/mount_path",
                             args=["xyz"],
                             sub_path="/sub/path/inside/mount_path",
                             hydro_program="example_hydrological_program",
                             description="sample description")

        # when
        yaml_gen = YamlJobGenerator(yaml_data)
        generated_yaml = yaml_gen.prepare_kubernetes_job()

        # then
        with open("data.yaml", 'r') as stream:
            expected_yaml = yaml.safe_load(stream)
            self.assertEqual(expected_yaml, generated_yaml, "Yaml files should be equal")
