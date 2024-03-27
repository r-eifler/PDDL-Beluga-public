import random
from typing import List, Tuple

from .jigs import Jig
from .rack import Rack
from .truck import Truck
from .flight import Flight
from .production_line import ProductionLine
from .beluga_problem_def import BelugaProblemDef
from . import utils

min_part_size = 2
max_part_size = 8

# min_rack_size = 10
# max_rack_size = 20

class BelugaRandomGenerator:

    def __init__(self, seed=None):
        self.random = random.Random(seed) if seed is not None else random.Random(0)

    def generate(self, num_jigs : int, num_racks : int , num_flights : int ,
                 num_production_lines : int , rack_space_factor : float):

        instance = BelugaProblemDef()

        instance.trucks_beluga.append(Truck('bt1',0))
        instance.trucks_factory += [Truck("ft1",0), Truck("ft2",0)]


        max_gen_part_size = 0

        for i in range(1, num_jigs + 1):
            size_loaded = self.random.randint(min_part_size, max_part_size)
            max_gen_part_size = max(max_part_size, size_loaded)
            size_empty = int(0.8 * size_loaded)
            instance.jigs.append(Jig(f"jig{utils.format_number(i, num_jigs)}", "base", size_empty, size_loaded))

        for i in range(0, num_production_lines):
            instance.production_lines.append(ProductionLine(f"pl{chr(i + 65)}"))

        self.generate_production_schedule(instance.jigs, instance.production_lines)

        fights = self.generate_flight_schedule(num_flights, instance.production_lines)
        instance.flights = fights


        total_rack_space = rack_space_factor * sum(j.size_loaded for j in instance.jigs)
        # print("Total rack space: " + str(total_rack_space))

        remaining_space = total_rack_space
        remaining_racks = num_racks

        for i in range(1, num_racks + 1):
            avg_rack_space = int(remaining_space / remaining_racks)
            deviation = int(avg_rack_space/3) if remaining_racks > 1  else 0
            size = max(max_gen_part_size, avg_rack_space + self.random.randint(- deviation, + deviation))
            remaining_space -= size
            remaining_racks -= 1
            instance.racks.append(Rack(f"rack{utils.format_number(i, num_racks)}", size))

        # print(instance.racks)

        return instance


    def generate_flight_schedule(self, num_flights: int, production_lines: List[ProductionLine]):

        pls = [] 
        for pl in production_lines:
            pls.append(pl.schedule.copy())
        linear = []
        while (sum([len(pl) for pl in pls]) > 0 ):
            next = self.random.randint(0,len(pls) - 1)
            linear.append(pls[next].pop(0))
            if len(pls[next]) == 0:
                del pls[next]

        num_jigs_per_flight = len(linear)/num_flights

        waiting = []
        flights = []

        for i in range(num_flights):
            next_in = linear[int(i*num_jigs_per_flight):int((i+1) * num_jigs_per_flight)]
            waiting += next_in
            self.random.shuffle(waiting)
            next_out = []
            for _ in range(int(len(waiting)/2)):
                next_out.append(waiting.pop())

            self.random.shuffle(next_in)
            self.random.shuffle(next_out)
            flights.append(Flight("beluga" + str(i), next_in, next_out))

        return flights


    def generate_production_schedule(self, jigs: List[Jig], production_lines : List[ProductionLine]) -> None:
        temp_list = list(jigs)
        self.random.shuffle(temp_list)
        while temp_list:
            part = temp_list.pop()
            pd = self.random.randint(0, len(production_lines) - 1)
            production_lines[pd].schedule.append(part)
