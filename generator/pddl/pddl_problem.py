from typing import List

from .pddl_literal import PDDLLiteral
from .pddl_param import PDDLParam

class PDDLProblem:
    def __init__(self):
        self.comments_objects: List[str] = []
        self.objects: List[PDDLParam] = []
        self.comments_init: List[str] = []
        self.init: List[PDDLLiteral] = []
        self.comments_goals: List[str] = []
        self.goal: List[PDDLLiteral] = []

    def add_object(self, o : PDDLParam) -> None:
        self.objects.append(o)

    def add_init(self, l : PDDLLiteral) -> None:
        self.init.append(l)

    def add_goal(self, l : PDDLLiteral) -> None:
        self.goal.append(l)


    def to_pddl(self, name: str) -> str:
        s = f"(define\n\t(problem {name})\n\t(:domain beluga)\n"
        s += '\t; ' + "\n\t; ".join(self.comments_objects) + "\n"
        s += "  (:objects\n\t\t" + "\n\t\t".join(obj.to_pddl() for obj in self.objects) + "\n\t)\n"
        s += '\t; ' + "\n\t; ".join(self.comments_init) + "\n"
        s += "  (:init\n\t\t" + "\n\t\t".join(init.to_pddl() for init in self.init) + "\n\t)\n"
        s += '\t; ' + "\n\t; ".join(self.comments_goals) + "\n"
        s += "  (:goal (and\n\t\t" + "\n\t\t".join(goal.to_pddl() for goal in self.goal) + "\n\t))\n"
        s += "  (:metric minimize (total-cost))\n"
        s += ")"
        return s