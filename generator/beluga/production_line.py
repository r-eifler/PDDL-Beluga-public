from .jigs import Jig
from typing import List

class ProductionLine:

    def __init__(self, name, schedule=[]) -> None:
        self.name = name
        self.schedule : List[Jig] = schedule