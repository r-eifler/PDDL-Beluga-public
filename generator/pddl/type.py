class Type:
    def __init__(self, name, base_type):
        self.name = name
        self.base_type = base_type

    def to_pddl(self):
        return f"{self.name} - {self.base_type}"