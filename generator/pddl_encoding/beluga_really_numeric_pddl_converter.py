from ..beluga.beluga_problem_def import BelugaProblemDef
from ..beluga import  utils
from pddl import PDDLProblem, PDDLPredicate, PDDLParam, PDDLNumericPredicate, DummyPDDLPredicate

from encoding_features import EncodingFeatures



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

        #### INIT 

        #TRUCKS
        problem.add_init(PDDLPredicate("empty", "t1"))
        problem.add_init(PDDLPredicate("atside", "t1", "bside"))
        problem.add_init(PDDLPredicate("empty", "t2"))
        problem.add_init(PDDLPredicate("atside", "t2", "fside"))
        problem.add_init(DummyPDDLPredicate())

        #parts
        for part in beluga_problem.parts:
            problem.add_init(PDDLNumericPredicate("=", "size " + part.name, part.size))
        problem.add_init(DummyPDDLPredicate())

        #RACKS
        for rack in beluga_problem.racks:
            problem.add_init(PDDLPredicate("not-pline", rack.name))
            problem.add_init(PDDLPredicate("not-beluga", rack.name))
            problem.add_init(PDDLPredicate("atside", rack.name, "bside"))
            problem.add_init(PDDLPredicate("atside", rack.name, "fside"))
            problem.add_init(PDDLNumericPredicate("=", "freespace " + rack.name, str(rack.size)))
            problem.add_init(PDDLNumericPredicate("=", "next " + rack.name + " bside", "0"))
            problem.add_init(PDDLNumericPredicate("=", "next " + rack.name + " fside", "0"))
            problem.add_init(DummyPDDLPredicate())
        problem.add_init(DummyPDDLPredicate())


        #BELUGAS  
        problem.add_init(PDDLPredicate("not-pline", "beluga"))
        problem.add_init(PDDLPredicate("atside", "beluga", "bside"))
        problem.add_init(PDDLNumericPredicate("=", "freespace beluga", "0"))
        problem.add_init(PDDLNumericPredicate("=", "next beluga bside", str(len(beluga_problem.arrivals))))
        problem.add_init(PDDLNumericPredicate("=", "next beluga fside", "0"))
        problem.add_init(DummyPDDLPredicate())

        
        # Arrival order
        problem.comments_init.append("Beluga arrival order:")

        for i, p in enumerate(beluga_problem.arrivals):
            problem.comments_init.append(str(i) + ": " + p.name)
        
        num_arriving_parts = len(beluga_problem.arrivals)
        for i, p in enumerate(beluga_problem.arrivals):
            problem.add_init(PDDLPredicate("in", p.name, "beluga"))
            problem.add_init(PDDLNumericPredicate("=", "pos " + p.name + " bside", str(num_arriving_parts - i)))
        problem.add_init(DummyPDDLPredicate())


        # Production Lines
        for pl in beluga_problem.production_lines:
            problem.add_init(PDDLPredicate("not-beluga", pl.name))
            problem.add_init(PDDLPredicate("atside", pl.name, "fside"))
            problem.add_init(PDDLNumericPredicate("=", "next " + pl.name + " bside", "0"))
            problem.add_init(PDDLNumericPredicate("=", "next " + pl.name + " fside", "0"))

            max_size_necessary = sum([p.size for p in pl.schedule])
            problem.add_init(PDDLNumericPredicate("=", "freespace " + pl.name, str(max_size_necessary)))
        problem.add_init(DummyPDDLPredicate())


        # total action cost
        problem.add_init(PDDLNumericPredicate("=", "total-cost", "0"))


        ##### GOAL
        for pl in beluga_problem.production_lines:

            problem.comments_goals.append("delivery order line " + pl.name + ": ")
            for i, p in enumerate(pl.schedule):
                problem.comments_goals.append(str(i) + ": " + p.name)

            for i, p in enumerate(pl.schedule):
                problem.add_goal(PDDLPredicate("in", pl.schedule[i].name, pl.name))
                problem.add_goal(PDDLNumericPredicate("=", "pos " + p.name + " fside", str(i + 1)))
    
        return problem
