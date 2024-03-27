from ..beluga.beluga_problem_def import BelugaProblemDef
from ..beluga import  utils
from pddl import PDDLProblem, PDDLPredicate, PDDLParam, PDDLNumericPredicate

from encoding_features import EncodingFeatures, RackEncoding, SoftGoals



def convert(beluga_problem : BelugaProblemDef, encoding_features : EncodingFeatures) -> PDDLProblem:

        problem = PDDLProblem();

        #### OBJECTS

        problem.add_object(PDDLParam("t1", "truck"))
        problem.add_object(PDDLParam("t2", "truck"))

        for r in beluga_problem.racks:
            problem.add_object(PDDLParam(r.name, "rack"))

        for p in beluga_problem.parts:
            problem.add_object(PDDLParam(p.name, "part"))

        for pl in beluga_problem.production_lines:
            problem.add_object(PDDLParam(pl.name, "rack"))

        problem.add_object(PDDLParam("beluga", "rack"))

        if encoding_features.no_constants_support:
            problem.add_object(PDDLParam("bside", "side"))
            problem.add_object(PDDLParam("fside", "side"))


        #### INIT 

        #equality 
        if encoding_features.no_equals_support:
            problem.add_init(PDDLPredicate("equal", "bside", "bside"))
            problem.add_init(PDDLPredicate("equal", "fside", "fside"))

            for p in beluga_problem.parts:
                problem.add_init(PDDLPredicate("equal", p.name, p.name))

        part_sizes = set([p.size for p in beluga_problem.parts])
        rack_sizes = set([r.size for r in beluga_problem.racks])
        max_rack_size = max(rack_sizes)
        sum_part_sizes = sum([p.size for p in beluga_problem.parts])
        max_needed_number = max(max_rack_size,sum_part_sizes)
        # print("Max needed number: " + str(max_needed_number))


        if encoding_features.number_encoding == RackEncoding.CLASSIC_BLOCKSWORLD:
                        
            numbers = utils.get_necessary_numbers(part_sizes, max_needed_number)

            for n in numbers:
                if n > 0:
                    problem.add_object(PDDLParam("n" + utils.format_number(n, max_needed_number), "num"))


            for rack in beluga_problem.racks:
                # print("Rack size: " + rack.name + " " + str(rack.size))
                for n1 in numbers:
                    for n2 in  part_sizes:
                        if (n1 + n2 <= rack.size):
                            # print(str(n1) + " " + str(n2))
                            problem.add_init(PDDLPredicate("fit-n-sum", 
                                " n" + utils.format_number(n1, max_needed_number),
                                " n" + utils.format_number(n2, max_needed_number),
                                " n" + utils.format_number(n1 + n2, max_needed_number),
                                rack.name))

            problem.add_init(PDDLPredicate("level", "beluga", "n" + utils.format_number(sum_part_sizes, max_needed_number)))
            for n1 in numbers:
                    for n2 in  part_sizes:
                        if (n1 + n2 <= sum_part_sizes):
                            problem.add_init(PDDLPredicate("fit-n-sum", 
                                " n" + utils.format_number(n1, max_needed_number),
                                " n" + utils.format_number(n2, max_needed_number),
                                " n" + utils.format_number(n1 + n2, max_needed_number),
                                "beluga"))
                            



        problem.add_init(PDDLPredicate("empty", "t1"))
        problem.add_init(PDDLPredicate("atside", "t1", "bside"));
        problem.add_init(PDDLPredicate("empty", "t2"))
        problem.add_init(PDDLPredicate("atside", "t2", "fside"));

        # PARTS
        for part in beluga_problem.parts:
            problem.add_init(PDDLPredicate("in", part.name, "beluga"))
        
        # Arrival order
        # bside 4   3   2   1   0   fside
        # print([p.name for p in beluga_problem.arrivals])
        # print(beluga_problem.arrivals[0].name)
        problem.add_init(PDDLPredicate("clear", beluga_problem.arrivals[0].name, "bside"))
        problem.add_init(PDDLPredicate("clear", beluga_problem.arrivals[-1].name, "fside"))
        problem.comments_init.append("Beluga arrival order:")
        for i, p in enumerate(beluga_problem.arrivals):
            problem.comments_init.append(str(i) + ": " + p.name)
        for i in range(len(beluga_problem.arrivals) - 1):
            problem.add_init(PDDLPredicate("on",  beluga_problem.arrivals[i].name, beluga_problem.arrivals[i+1].name, "bside"))
            problem.add_init(PDDLPredicate("on",  beluga_problem.arrivals[i+1].name, beluga_problem.arrivals[i].name, "fside"))


        #RACKS
        for rack in beluga_problem.racks:
            problem.add_init(PDDLPredicate("not-pline", rack.name))
            problem.add_init(PDDLPredicate("not-beluga", rack.name))
            problem.add_init(PDDLPredicate("empty", rack.name));
            problem.add_init(PDDLPredicate("atside", rack.name, "bside"));
            problem.add_init(PDDLPredicate("atside", rack.name, "fside"));
            
        problem.add_init(PDDLPredicate("not-pline", "beluga"))
        problem.add_init(PDDLPredicate("atside", "beluga", "bside"));

        #RACK and PART sizes
        if encoding_features.number_encoding == RackEncoding.CLASSIC_BLOCKSWORLD:
            for part in beluga_problem.parts:
                problem.add_init(PDDLPredicate("size", part.name, "n" + utils.format_number(part.size, max_needed_number)))
            for rack in beluga_problem.racks:
                problem.add_init(PDDLPredicate("level", rack.name, "n" + utils.format_number(0, max_needed_number)))

        else:
            for part in beluga_problem.parts:
                problem.add_init(PDDLNumericPredicate("=", "size " + part.name, part.size))

            for rack in beluga_problem.racks:
                problem.add_init(PDDLNumericPredicate("=", "level " + rack.name, "0"))
                problem.add_init(PDDLNumericPredicate("=", "max-level " + rack.name, str(rack.size)))
                
            problem.add_init(PDDLNumericPredicate("=", "level beluga", str(sum_part_sizes)));
            problem.add_init(PDDLNumericPredicate("=", "max-level beluga", str(sum_part_sizes)))
        
        # Production Lines
        for pl in beluga_problem.production_lines:
            problem.add_init(PDDLPredicate("not-beluga", pl.name))
            problem.add_init(PDDLPredicate("atside", pl.name, "fside"))
            problem.add_init(PDDLPredicate("empty", pl.name))

            max_size_nacessary = sum([p.size for p in pl.schedule])
            if encoding_features.number_encoding == RackEncoding.CLASSIC_BLOCKSWORLD:

                for n1 in numbers:
                    for n2 in  part_sizes:
                        if (n1 + n2 <= max_size_nacessary):
                            problem.add_init(PDDLPredicate("fit-n-sum", 
                                " n" + utils.format_number(n1, max_needed_number),
                                " n" + utils.format_number(n2, max_needed_number),
                                " n" + utils.format_number(n1 + n2, max_needed_number),
                                pl.name))

                problem.add_init(PDDLPredicate("level", pl.name, "n" + utils.format_number(0, max_needed_number)))

            else:
                problem.add_init(PDDLNumericPredicate("=", "level " + pl.name, str(0)))
                problem.add_init(PDDLNumericPredicate("=", "max-level " + pl.name, str(max_size_nacessary)))


        # total action cost
        problem.add_init(PDDLNumericPredicate("=", "total-cost", "0"))


        ##### GOAL
        for pl in beluga_problem.production_lines:
            problem.comments_goals.append("delivery order line " + pl.name + ": ")
            for i, p in enumerate(pl.schedule):
                problem.comments_goals.append(str(i) + ": " + p.name)
            for i in range(len(pl.schedule) - 1):
                problem.add_goal(PDDLPredicate("on",  pl.schedule[i+1].name, pl.schedule[i].name, "fside"))
                problem.add_goal(PDDLPredicate("in",  pl.schedule[i].name, pl.name));
            problem.add_goal(PDDLPredicate("in",  pl.schedule[-1].name, pl.name));
        
        if SoftGoals.USED_RACKS in encoding_features.soft_goals:
            for rack in beluga_problem.racks:
                problem.aadd_goal(PDDLPredicate("unused", rack.name))

        if SoftGoals.NUM_SWAPS in encoding_features.soft_goals:
            nums_swap = ["ns" + utils.format_number(i, encoding_features.max_num_swaps) for i in range(encoding_features.max_num_swaps)]
            for n in  nums_swap:
                problem.add_goal(PDDLPredicate("num-swaps", n.name))
    
        return problem
