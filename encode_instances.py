import sys, os

import argparse
import tomllib

parser = argparse.ArgumentParser(description="Encode json problem in PDDL")

parser.add_argument('-c', dest="config_file", help="toml configuration file", required=True)
parser.add_argument('-i', help="inout folder of json problem definition", default=None, required=True)
parser.add_argument('-o', help="output folder to store problem files", default=None, required=True)
parser.add_argument('-y', dest="no_questions", help="just run", action='store_true' , required=False)

args = parser.parse_args()

out_folder = args.o
input_folder = args.i

with open(args.config_file, "rb") as f:
    config = tomllib.load(f)

encoding = config["encoding"]
beluga = config["beluga"]
factory = config["factory"]
features = config["features"]

final_num_instances = len(os.listdir(input_folder))

if not args.no_questions:
    print("Do you want to encode " + str(final_num_instances) + " instances? y/n")
    answer = input()

    if answer != "y":
        exit()

num_instances = 0

# os.system("rm " + out_folder + "/*")

instance_params = [
    '-e', encoding,
    '-b', beluga,
    '-f', factory,
    '-o', out_folder,
]

if len(features) > 0:
    instance_params += ['-x', " ".join(features)]

#gen domain
args = ["./generator/json2PDDL.py", "-d"] + instance_params
print(args)
os.system(" ".join(args))

#gen instances
for problem in os.listdir(input_folder):
    if num_instances % 10 == 0:
        print(str(num_instances) + "/" + str(final_num_instances))
    
    final_params = instance_params +  [
        '-i', os.path.join(input_folder, problem),
    ]

    args = ["./generator/json2PDDL.py"] + final_params

    os.system(" ".join(args))
    num_instances += 1


print("Number of encoded instances: " + str(num_instances))

