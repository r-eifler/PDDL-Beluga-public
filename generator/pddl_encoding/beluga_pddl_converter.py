from ..beluga.beluga_problem_def import BelugaProblemDef
from ..beluga import  utils
from pddl import PDDLProblem, PDDLPredicate, PDDLParam, PDDLNumericPredicate

from encoding_features import EncodingFeatures, RackEncoding, SoftGoals



def convert(beluga_problem : BelugaProblemDef, encoding_features : EncodingFeatures) -> PDDLProblem:

        problem = PDDLProblem();

        #### OBJECTS

        problem.add_object(PDDLParam("t1", "beluga-truck"))
        problem.add_object(PDDLParam("t2", "factory-truck"))

        for r in beluga_problem.racks:
            problem.add_object(PDDLParam(r.name, "rack"))

        for p in beluga_problem.parts:
            problem.add_object(PDDLParam(p.name, "part"))

        for pl in beluga_problem.production_lines:
            problem.add_object(PDDLParam(pl.name, "production-line"))


        #### INIT 
        part_sizes = set([p.size for p in beluga_problem.parts])
        rack_sizes = set([r.size for r in beluga_problem.racks])
        max_rack_size = max(rack_sizes)

        problem.add_init(PDDLPredicate("empty", "t1"));
        problem.add_init(PDDLPredicate("empty", "t2"));

        if encoding_features.number_encoding == RackEncoding.CLASSIC_BLOCKSWORLD:
                            
            numbers = utils.get_necessary_numbers(part_sizes, max_rack_size)

            for n in numbers:
                if n > 0:
                    problem.add_object(PDDLParam("n" + utils.format_number(n, max_rack_size), "num"))


            for rack in beluga_problem.racks:
                for n1 in numbers:
                    for n2 in  part_sizes:
                        if (n1 + n2 <= rack.size):
                            problem.add_init(PDDLPredicate("fit-n-sum", 
                                " n" + utils.format_number(n1, max_rack_size),
                                " n" + utils.format_number(n2, max_rack_size),
                                " n" + utils.format_number(n1 + n2, max_rack_size),
                                rack.name))
   
            if SoftGoals.NUM_SWAPS in encoding_features.soft_goals and encoding_features.max_num_swaps > 0:
            
                nums_swaps = []
                for i in range(encoding_features.max_num_swaps):
                    name = "ns" + utils.format_number(i, encoding_features.max_num_swaps)
                    nums_swaps.append(name);
                    problem.add_object(PDDLParam(name, "num-sw"))
                
                for i in range(encoding_features.max_num_swaps - 1):
                    problem.add_init(PDDLPredicate("next", nums_swaps[i], nums_swaps[i+1]))

                problem.add_init(PDDLPredicate("num-swaps", nums_swaps[0]))


        # PARTS
        for part in beluga_problem.parts:
            problem.add_init(PDDLPredicate("on-rack", "noner", part.name));
            problem.add_init(PDDLPredicate("no-rack-succ", part.name));
            problem.add_init(PDDLPredicate("no-rack-pre", part.name));
        

        problem.add_init(PDDLPredicate("ready-to-unload", beluga_problem.arrivals[0].name));
        for i in range(len(beluga_problem.arrivals)):
            if i < len(beluga_problem.arrivals) - 1:
                problem.add_init(PDDLPredicate("next-to-unload",  beluga_problem.arrivals[i].name,  beluga_problem.arrivals[i+1].name));
            else:
                problem.add_init(PDDLPredicate("next-to-unload",  beluga_problem.arrivals[i].name, "nonep"));


        #RACKS
        for rack in beluga_problem.racks:
            problem.add_init(PDDLPredicate("unused", rack.name))
            

        #RACK and PART sizes
        if encoding_features.number_encoding == RackEncoding.CLASSIC_BLOCKSWORLD:
            for part in beluga_problem.parts:
                problem.add_init(PDDLPredicate("size", part.name, "n" + utils.format_number(part.size, max_rack_size)))
            for rack in beluga_problem.racks:
                problem.add_init(PDDLPredicate("level", rack.name, "n" + utils.format_number(0, rack.size)))
        else:
            problem.add_init(PDDLNumericPredicate("=", "size nonep", "0"))
            problem.add_init(PDDLNumericPredicate("=", "level noner", "0"));
            problem.add_init(PDDLNumericPredicate("=", "max-level noner", "0"));
            for part in beluga_problem.parts:
                problem.add_init(PDDLNumericPredicate("=", "size " + part.name, part.size))
            for rack in beluga_problem.racks:
                problem.add_init(PDDLNumericPredicate("=", "level " + rack.name, "0"));
                problem.add_init(PDDLNumericPredicate("=", "max-level " + rack.name, str(rack.size)));


        #production schedule
        for pl in beluga_problem.production_lines:

            if len(pl.schedule) == 0:
                problem.add_init(PDDLPredicate("p-line-next", pl.name, "nonep"));
            else:
                problem.add_init(PDDLPredicate("p-line-next", pl.name, pl.schedule[0].name));
                for i in range(len(pl.schedule) - 1):
                    problem.add_init(PDDLPredicate("p-line-succ", pl.schedule[i].name, pl.schedule[i+1].name));
                problem.add_init(PDDLPredicate("p-line-succ", pl.schedule[-1].name, "nonep"));

        # problem.add_init(PDDLPredicate("p-line-succ", "nonep", "nonep"));


        # total action cost
        problem.add_init(PDDLNumericPredicate("=", "total-cost", "0"))


        ##### GOAL
        for part in beluga_problem.parts:
            problem.add_goal(PDDLPredicate("processed", part.name));
        
        if SoftGoals.USED_RACKS in encoding_features.soft_goals:
            for rack in beluga_problem.racks:
                problem.add_goal(PDDLPredicate("unused", rack.name))

        if SoftGoals.NUM_SWAPS in encoding_features.soft_goals:
            nums_swap = ["ns" + utils.format_number(i, encoding_features.max_num_swaps) for i in range(encoding_features.max_num_swaps)]
            for n in  nums_swap:
                problem.add_goal(PDDLPredicate("num-swaps", n))
    
        return problem
