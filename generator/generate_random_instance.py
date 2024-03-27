#!/usr/bin/env python


import argparse
import json
from beluga import BelugaRandomGenerator
from beluga.beluga_problem_def import BelugaProblemDefEncoder
from encoding_features import EncodingFeatures




def main():
    parser = argparse.ArgumentParser(description='Description of your program')

    parser.add_argument('-j', '--num_jigs', type=int, help='Number of jigs', required=True)
    parser.add_argument('-r', '--num_racks', type=int, help='Number of racks', required=True)
    parser.add_argument('--rack_space_factor', type=float, required=False, default=2,
                        help='Defines how much space is on the racks, compared to the sum of part sizes. \
                            sum(rack_sizes) = x * sum(part_sizes)'
                        )
    parser.add_argument('-pl', '--num_production_lines', type=int, required=False, help='Number of production lines', default=1)
    parser.add_argument('-s', '--seed', type=int, required=False, help='Seed value', default=0)
    parser.add_argument('-f', '--flights', type=int, required=False, help='number of flights', default=1)

    parser.add_argument('-o', '--out', type=str, required=False, help='Output file for the problem')

    args = parser.parse_args()

    num_jigs = args.num_jigs
    num_racks = args.num_racks
    num_production_lines = args.num_production_lines
    seed = args.seed
    problem_out = args.out
    rack_space_factor = args.rack_space_factor
    num_flights = args.flights

    generator = BelugaRandomGenerator(seed)

    inst = generator.generate(num_jigs, num_racks, num_flights, num_production_lines, rack_space_factor)

    if problem_out:
        with open(problem_out, 'w') as out_file:
            json.dump(inst, out_file, cls=BelugaProblemDefEncoder, indent=4)
    else:
        print(json.dumps(inst))


if __name__ == "__main__":
    main()