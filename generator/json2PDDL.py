#!/usr/bin/env python

import json
import argparse
import os
from pddl_encoding import DomainEncoding
from pddl_encoding import convert
from encoding_features import FeatureOptions, EncodingOptions, EncodingFeatures
from beluga.beluga_problem_def import BelugaProblemDefDecoder


def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-o', '--problem-out', dest="problem_out", type=str, required=False, help='Output folder for the problem/domain')
    parser.add_argument('-d', '--gen-domain-file', dest="gen_domain_file", required=False, action='store_true', 
                        help='generate domain file for encoding and feature combination')
    parser.add_argument('-i', '--instance', help='instance to encode', required=False)

    parser.add_argument('-e', '--encoding', dest="encoding", type=EncodingOptions, 
                        choices=[EncodingOptions.NUMERIC, EncodingOptions.CLASSIC], 
                        required=False, default=EncodingOptions.CLASSIC, help='general encoding')
    parser.add_argument('-b', '--beluga', dest="beluga", type=EncodingOptions, 
                        choices=[EncodingOptions.BELUGA_RACK, EncodingOptions.BELUGA_SPECIAL], 
                        required=False, default=EncodingOptions.BELUGA_SPECIAL, 
                        help='encode beluga either as rack or use separate encoding with special actions')
    parser.add_argument('-f', '--factory', dest="factory", type=EncodingOptions, 
                    choices=[EncodingOptions.FACTORY_RACK, EncodingOptions.FACTORY_SPECIAL], 
                    required=False, default=EncodingOptions.FACTORY_SPECIAL, 
                    help='encode factory production lines either as racks or use separate encoding with special actions')
    

    parser.add_argument('-x', '--features', dest="features", type=FeatureOptions, nargs='+', 
                    required=False, default=[], 
                    help='features that the model should support')
    

    args = parser.parse_args()

    instance_file = args.instance

    gen_domain_file = args.gen_domain_file
    problem_out = args.problem_out

    encoding_features = EncodingFeatures()
    encoding_features.encoding = args.encoding
    encoding_features.beluga = args.beluga
    encoding_features.factory = args.factory

    encoding_features.feature_options = args.features

    if gen_domain_file:
        domain_encoding = DomainEncoding(encoding_features)
        name = 'beluga'
        if problem_out:
            with open(os.path.join(problem_out, "domain.pddl"), 'w') as out_file:
                out_file.write(domain_encoding.domain.to_pddl(name))
        else:
            print(domain_encoding.domain.to_pddl(name))
        return


    with open(instance_file, 'r') as fp:
        inst = json.load(fp, cls=BelugaProblemDefDecoder)

    pddl_problem = convert(inst, encoding_features)

    problem_name = os.path.basename(instance_file).replace(".json","")

    name = "beluga-" + problem_name
    if problem_out:
        with open(os.path.join(problem_out, problem_name + ".pddl"), 'w') as out_file:
            out_file.write(pddl_problem.to_pddl(name))
    else:
        print(pddl_problem.to_pddl(name))


if __name__ == "__main__":
    main()