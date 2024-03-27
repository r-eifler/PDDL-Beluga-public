from typing import List

from .type import Type
from .pddl_predicate import PDDLPredicate
from .pddl_action import PDDLAction
from .pddl_literal import PDDLLiteral

class PDDLDomain:
    def __init__(self):
        self.requirements: List[str] = [":typing", ":fluents", ":equality", ":action-costs"]
        self.types : List[Type] = []
        self.constants : List[PDDLLiteral] = []
        self.predicates : List[PDDLPredicate] = []
        self.functions : List[PDDLLiteral] = []
        self.actions : List[PDDLAction] = []

    def to_pddl(self, name: str) -> str:
        s = f"(define (domain {name})\n"
        s += f"  (:requirements {' '.join(self.requirements)})\n"
        s += "  (:types\n\t\t" + "\n\t\t".join(type_.to_pddl() for type_ in self.types) + "\n)\n"
        s += "  (:constants\n\t\t" + "\n\t\t".join(constant.to_pddl() for constant in self.constants) + "\n\t)\n\n\n"
        s += "  (:predicates\n\t\t" + "\n\t\t".join(predicate.to_pddl() for predicate in self.predicates) + "\n\t)\n\n\n"
        s += "  (:functions\n\t\t" + "\n\t\t".join(f"{function.to_pddl()}" for function in self.functions) + "\n\t)\n\n\n"
        s += "\n\n\n".join(action.to_pddl() for action in self.actions)
        s += ")"
        return s