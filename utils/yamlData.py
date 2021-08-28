class YamlData:

    def __init__(self, pod_name, container_image, container_name,
                 mount_path, mount_path_name, args, volumes_host_path):
        self.pod_name = pod_name
        self.container_image = container_image
        self.container_name = container_name
        self.mount_path = mount_path
        self.mount_path_name = mount_path_name
        self.args = args
        self.volumes_host_path = volumes_host_path
