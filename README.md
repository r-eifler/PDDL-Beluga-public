# Beluga Problem Generator and PDDL Encoder

This repository provides scripts to 

1. generate random Beluga problem instances 
2. encode a Beluga problem instances in PDDL (classic and numeric)

## Problem Generator

The problem generator generates a random Beluga instances and stores it in a JSON file.
The generator does **not ensure solvability**.

The following parameter can be specified:

* number of jigs
* number of racks
* number of production lines (default 1)
* number of flights in the flight schedule
* rack space factor (sum(rack_sizes) = x * sum(part_sizes))
* seed (affects the flight and production schedule)

A single problem can be generated with:

    generate_random_instance.py -r 2 -j 4


If no output file is specified, that the JSON in written to `stdout`.

To generate multiple instances with increasing number of racks and jigs 
use the script:

    generate_instances.py -c config_files/test_c_20_50.toml -o <out_folder> -i <json problem folder>


The parameters are defined in a `toml` file.
You can find examples in `config_files`.

## PDDL Encoding

We provide a **classical** as well as a **numeric** PDDL encoding.

We support the following encoding options:

Numbers to encode the rack space and jig size are either defined with functions (NUMERIC)
or with objects and predicates (CLASSIC)

    encoding = "CLASSIC" or "NUMERIC"

The belugas and the factory are either encoded the same way as the racks 
or are encoded individually (own actions and no modeling of their size)

    beluga = "BELUGA_SPECIAL" or "BELUGA_RACK"
    factory = "FACTORY_SPECIAL" or "FACTORY_RACK"


The racks can either be modeled as a linked list with predicates indicating the 
predecessor and successor jig or as an array with indices and pointers to the 
next free position.

    rack_encoding = "LINKED_LIST" or "POSITION_POINTER"

### Features 
The most basic version includes required the jigs to be unloaded from a single 
Beluga and delivered to the factory in the correct order.
On top of that we support any subset of the following features:

    features = ["OUTGOING_EMPTY_JIGS", "FLIGHT_SCHEDULE", "TRUCK_CAPACITY", "DRIVING"]

* `OUTGOING_EMPTY_JIGS`: If a jig is delivered to the factory it becomes empty and shorter
and needs then to be loaded back into the beluga (unloaded and loading can be done in 
parallel)
* `FLIGHT_SCHEDULE`: Instead of just one Beluga, we have multiple flights (models planning horizon)
each flight has to be completely unloaded and loaded before the next one becomes available
* `TRUCK_CAPACITY`: The trucks can not only transport on jig at a time, but instead function like a mobile 
rack with a size and ordered jigs. (TODO)
* `DRIVING`: The trucks have to perform a drive action to move between the beluga 
hanger the racks and the factory. (TODO)

To encode multiple instances use the script:

    encode_instances.py -c config_files/small_test_encoding.toml -o <out_folder> -i <json problem folder>

The encoding parameters and features are defined in a `toml` file.
You can find examples in `config_files`.
