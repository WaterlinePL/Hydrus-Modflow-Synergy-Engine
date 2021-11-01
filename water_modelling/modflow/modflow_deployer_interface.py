class IModflowDeployer:

    def run(self):
        """
        Run Modflow simulation (in an abstract way). This method is not supposed to be called, it indicates that
        a proper Modflow simulation deployer should implement it.
        @return: None
        """
        raise Exception("Unimplemented method!")
