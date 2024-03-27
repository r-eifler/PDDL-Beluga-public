from .jigs import Jig
from typing import List

class Flight:

    def __init__(self, name, incoming=[], outgoing=[]) -> None:
        self.name = name
        self.incoming : List[Jig] = incoming
        self.outgoing : List[Jig] = outgoing