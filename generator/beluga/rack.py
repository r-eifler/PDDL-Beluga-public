class Rack:

    def __init__(self, name: str, size : int) -> None:
        self.name = name
        self.size = size

    def __repr__(self) -> str:
        return self.name + " --> " + str(self.size)