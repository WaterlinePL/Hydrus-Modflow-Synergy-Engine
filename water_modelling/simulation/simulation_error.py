class SimulationError:

    def __init__(self, model_name: str, error_description: str):
        self.model_name = model_name
        self.error_description = error_description

    def __str__(self):
        return f"{self.model_name}: {self.error_description}"
