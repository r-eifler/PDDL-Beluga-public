from abc import ABC, abstractmethod

class PDDLLiteral(ABC):
    @abstractmethod
    def to_pddl(self) -> str:
        pass