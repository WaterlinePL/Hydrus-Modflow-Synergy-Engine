
class IHydrusDeployer:

    def run(self):
        """
        Run Hydrus simulation (in an abstract way). This method is not supposed to be called, it indicates that
        a proper Hydrus simulation deployer should implement it.
        @return: None
        """
        raise Exception("Unimplemented method!")
