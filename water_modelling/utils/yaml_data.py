from typing import List


class YamlData:

    def __init__(self, job_name: str, container_image: str, container_name: str,
                 mount_path: str, args: List[str], sub_path: str):

        self.job_name = job_name
        self.container_image = container_image
        self.container_name = container_name
        self.mount_path = mount_path
        self.args = args
        self.sub_path = sub_path
