from typing import List

from .pddl_literal import PDDLLiteral
from .pddl_param import PDDLParam


class PDDLAction:
    def __init__(self, name: str):
        self.name = name
        self.parameters : List[PDDLParam] = []
        self.preconditions : List[PDDLLiteral]  = []
        self.effects : List[PDDLLiteral] = []

    def add_parameter(self, p: PDDLParam):
        self.parameters.append(p)

    def add_precondition(self, l: PDDLLiteral):
        self.preconditions.append(l)

    def add_effect(self, l: PDDLLiteral):
        self.effects.append(l)

    def to_pddl(self) -> str:
        s = f"\t(:action {self.name}\n"
        s += f"\t\t:parameters ({' '.join(param.to_pddl() for param in self.parameters)})\n"
        s += "\t\t:precondition (and\n\t\t\t"
        s += '\n\t\t\t'.join(precondition.to_pddl() for precondition in self.preconditions)
        s += "\n\t\t)\n"
        s += "\t\t:effect (and\n\t\t\t"
        s += '\n\t\t\t'.join(effect.to_pddl() for effect in self.effects)
        s += "\n\t\t)\n\t)\n\n\n"
        return s