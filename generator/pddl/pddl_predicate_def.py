from typing import List
from pddl.pddl_predicate import PDDLPredicate
from pddl.pddl_literal import PDDLLiteral
from pddl.pddl_param import PDDLParam

class PDDLPredicateDef(PDDLLiteral):
    def __init__(self, name: str, *args: PDDLParam):
        self.name = name
        self.args: List[PDDLParam] = list(args)

    def to_pddl(self) -> str:
        return f"({self.name} {' '.join(arg.to_pddl() for arg in self.args)})"
    
    def gp(self, *args: PDDLParam):
        #TODO check arg types
        return PDDLPredicate(self.name, *args)
    
    def gp_neg(self, *args: PDDLParam):
        #TODO check arg types
        return PDDLPredicate(self.name, *args, negated = True)
    