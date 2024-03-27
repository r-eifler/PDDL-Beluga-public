from typing import List
import json

from .flight import Flight
from .truck import Truck

from .rack import Rack
from .jigs import Jig
from .production_line import ProductionLine

class BelugaProblemDef:

    def __init__(self):

        self.trucks_beluga : List[Truck] = []
        self.trucks_factory : List[Truck] = []

        self.racks : List[Rack] = []
        self.jigs : List[Jig] = []

        self.flights : List[Flight] = []

        self.hanger =  ["hanger1"]
        self.production_lines : List[ProductionLine] = []


class BelugaProblemDefEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Rack, Jig, ProductionLine, Truck, Flight)):
            return obj.__dict__
        elif isinstance(obj, BelugaProblemDef):
            return {
                'trucks_beluga': obj.trucks_beluga,
                'trucks_factory': obj.trucks_factory,
                'racks': obj.racks,
                'jigs': obj.jigs,
                'production_lines': obj.production_lines,
                'flights': obj.flights
            }
        return super().default(obj)
    
    
class BelugaProblemDefDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if 'name' in dct and 'type' in dct:
            if dct['type'] == 'Truck':
                return Truck(**dct)
            if dct['type'] == 'Rack':
                return Rack(**dct)
            elif dct['type'] == 'Part':
                return Jig(**dct)
            elif dct['type'] == 'ProductionLine':
                return ProductionLine(**dct)
            elif dct['type'] == 'Flight':
                    return Flight(**dct)
        elif 'trucks_beluga' in dct and 'trucks_factory' in dct and \
            'racks' in dct and 'jigs' in dct and \
            'production_lines' in dct and 'flights' in dct:
            instance = BelugaProblemDef()
            instance.trucks_beluga = [Truck(**t) for t in dct['trucks_beluga']]
            instance.trucks_factory = [Truck(**t) for t in dct['trucks_factory']]
            instance.racks = [Rack(**rack) for rack in dct['racks']]
            instance.jigs = [Jig(**jig) for jig in dct['jigs']]
            instance.flights = [Flight(f['name'], [Jig(**s) for s in f['incoming']], [Jig(**s) for s in f['outgoing']]) for f in dct['flights']]
            instance.production_lines = [ProductionLine(line['name'], [Jig(**s) for s in line['schedule']]) for line in dct['production_lines']]
            return instance
        return dct