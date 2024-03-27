from .pddl_literal import PDDLLiteral

class PDDLPredicate(PDDLLiteral):
    def __init__(self, name: str, *args: str, negated: bool = False):
        self.name = name
        self.args = list(args)
        self.negated = negated

    def to_pddl(self) -> str:
        s = ""
        if self.negated:
            s += "(not "
        s += f"({self.name} {' '.join(self.args)})"
        if self.negated:
            s += ")"
        return s
    


class DummyPDDLPredicate(PDDLLiteral):

    def __init__(self):
        pass

    def to_pddl(self) -> str:
        return ""