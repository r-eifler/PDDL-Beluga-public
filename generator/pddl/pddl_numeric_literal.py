from pddl.pddl_param import PDDLParam
from pddl.pddl_literal import PDDLLiteral

class PDDLNumericPredicate(PDDLLiteral):
    def __init__(self, fun: str, arg1: PDDLLiteral, arg2: PDDLLiteral):
        self.fun = fun
        self.arg1 = arg1
        self.arg2 = arg2

    def to_pddl(self) -> str:
        return f"({self.fun} {self.arg1.to_pddl()} {self.arg2.to_pddl()})"