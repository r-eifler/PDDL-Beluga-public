class PDDLParam:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def to_pddl(self) -> str:
        return f"{self.name} - {self.type}"
    

class PDDLNumericParam:
    def __init__(self, value: int):
        self.value = value

    def to_pddl(self) -> str:
        return f"({self.value})"
    
class PDDLNumericValue:
    def __init__(self, value: int):
        self.value = value

    def to_pddl(self) -> str:
        return f"{str(self.value)}"