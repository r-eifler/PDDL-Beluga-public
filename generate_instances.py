import sys, os

import argparse
import tomllib

parser = argparse.ArgumentParser(description="Generation random Beluga instances")

parser.add_argument('-c', dest="config_file", help="toml configuration file", required=True)
parser.add_argument('-y', dest="no_questions", help="just run", action='store_true' , required=False)
parser.add_argument('-o', help="output folder to store problem files", default=None, required=True)

args = parser.parse_args()

out_folder = args.o

with open(args.config_file, "rb") as f:
    config = tomllib.load(f)

seeds = config["seeds"]

min_num_jigs = config["min_num_jigs"]
max_num_jigs = config["max_num_jigs"]

min_num_racks = config["min_num_racks"]
max_num_racks = config["max_num_racks"]

# number of racks / number of parts
min_constraint = config["min_constraint"]
max_constraint = config["max_constraint"]

# sum of rack sizes / sum pf part sizes
rack_space_factors = config["rack_space_factors"]

flights = config["flights"]

final_num_instances = 0
for seed in seeds:
    for numParts in range(min_num_jigs, max_num_jigs + 1):
        for numRacks in range(min_num_racks, max_num_racks + 1):
            for rack_space_factor in rack_space_factors:
                c = numRacks / numParts
                if min_constraint <= c <= max_constraint:
                    final_num_instances += 1


if not args.no_questions:
    print("Do you want to generate " + str(final_num_instances) + " instances? y/n")
    answer = input()

    if answer != "y":
        exit()

num_instances = 0

os.system("rm " + out_folder + "/*")

for seed in seeds:
    for numParts in range(min_num_jigs, max_num_jigs + 1):
        for numRacks in range(min_num_racks, max_num_racks + 1):
            for rack_space_factor in rack_space_factors:
                c = numRacks / numParts
                if min_constraint <= c <= max_constraint:
                    if num_instances % 10 == 0:
                        print(str(num_instances) + "/" + str(final_num_instances))
                    out_file = out_folder + "/problem_" + "_".join([str(numParts), str(numRacks), str(int(rack_space_factor*10)), str(seed)]) + ".json"
                    instance_params = [
                        '-j', str(numParts), 
                        '-r', str(numRacks),
                        '-s', str(seed),
                        '-f', str(flights),
                        '--rack_space_factor', str(rack_space_factor),
                        '-o', out_file
                    ]

                    args = ["./generator/generate_random_instance.py"] + instance_params

                    os.system(" ".join(args))
                    num_instances += 1


print("Number of generated instances: " + str(num_instances))

