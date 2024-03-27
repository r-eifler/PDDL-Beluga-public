from enum import Enum
from typing import List

class EncodingOptions(Enum):

    CLASSIC = "CLASSIC"
    NUMERIC = "NUMERIC"
    
    RACK_LINKED_LIST = 'LINKED_LIST'
    RACK_POSITION_POINTER = 'POSITION_POINTER' # TODO

    COMBINED_MOVE = 'COMBINED_MOVE' # TODO
    LOAD_AND_UNLOAD = 'LOAD_AND_UNLOAD'

    BELUGA_RACK = 'BELUGA_RACK'
    BELUGA_SPECIAL = 'BELUGA_SPECIAL'

    FACTORY_RACK = 'FACTORY_RACK'
    FACTORY_SPECIAL = 'FACTORY_SPECIAL'
    

class FeatureOptions(Enum):
    
    OUTGOING_EMPTY_JIGS = 'OUTGOING_EMPTY_JIGS'
    FLIGHT_SCHEDULE = 'FLIGHT_SCHEDULE'
    TRUCK_CAPACITY = 'TRUCK_CAPACITY' #TODO
    DRIVING = 'DRIVING' 


class ModelTricks(Enum):
    
    RACK_RANKING = "RACK_RANKING"

class SoftGoals(Enum):

    USED_RACKS = 'USED_RACKS'
    NUM_SWAPS = 'NUM_SWAPS'
    PARTS_PROCESSED = 'PARTS_PROCESSED'

class EncodingFeatures:

    def __init__(self) -> None:

        self.encoding = EncodingOptions.NUMERIC
        
        self.rack_encoding : EncodingOptions = EncodingOptions.RACK_LINKED_LIST
        self.load_encoding : EncodingOptions = EncodingOptions.LOAD_AND_UNLOAD
        self.beluga : EncodingOptions = EncodingOptions.BELUGA_SPECIAL
        self.factory : EncodingOptions = EncodingOptions.FACTORY_SPECIAL

        self.feature_options : List[FeatureOptions] = []

        self.model_tricks : List[ModelTricks] = [] # = [ModelTricks.RACK_RANKING]

        self.deterministic : bool = True

        self.rack_space_factor = 2

        self.soft_goals : List[SoftGoals] = []
        self.max_num_swaps = 5

        self.no_constants_support = False
        self.no_equals_support = False
