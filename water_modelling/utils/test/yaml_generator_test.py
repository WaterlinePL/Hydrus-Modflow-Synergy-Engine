import unittest
import numpy as np
import yaml

from utils.yaml_data import YamlData
from utils.yaml_generator import YamlGenerator


class YamlGeneratorTest(unittest.TestCase):

    def test_should_create_yaml(self):

        # given
        yaml_data = YamlData(pod_name="pod_name",
                                 container_image="container_image",
                                 container_name="container_name",
                                 mount_path="/mount_path",
                                 mount_path_name="mount_path_name",
                                 args=["xyz"],
                                 volumes_host_path="/volumes_host_path")

        # when
        yaml_gen = YamlGenerator(yaml_data)
        generated_yaml = yaml_gen.prepare_kubernetes_pod()

        # then
        with open("data.yaml", 'r') as stream:
            expected_yaml = yaml.safe_load(stream)
            self.assertEqual(expected_yaml, generated_yaml, "Yaml files should be equal")
