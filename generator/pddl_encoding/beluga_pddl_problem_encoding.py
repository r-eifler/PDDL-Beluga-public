from encoding_features import FeatureOptions
from beluga.beluga_problem_def import BelugaProblemDef
from beluga import  utils
from pddl.pddl_param import PDDLNumericParam, PDDLNumericValue
from pddl import PDDLProblem, PDDLPredicate, PDDLParam, PDDLNumericPredicate

from encoding_features import EncodingFeatures, EncodingOptions, ModelTricks



def convert(beluga_problem : BelugaProblemDef, ef : EncodingFeatures) -> PDDLProblem:

        problem = PDDLProblem()

        #### OBJECTS
        for truck in beluga_problem.trucks_beluga + beluga_problem.trucks_factory:
            problem.add_object(PDDLParam(truck.name, "truck"))

        for r in beluga_problem.racks:
            problem.add_object(PDDLParam(r.name, "rack"))
        if  ModelTricks.RACK_RANKING in ef.model_tricks:
            problem.add_object(PDDLParam("dummy-rack", "rack"))

        for j in beluga_problem.jigs:
            problem.add_object(PDDLParam(j.name, "jig"))
        # if (ef.beluga == EncodingOptions.BELUGA_SPECIAL or ef.factory == EncodingOptions.FACTORY_SPECIAL) and \
        #     ef.encoding == EncodingOptions.CLASSIC:
        #     problem.add_object(PDDLParam("dummy-jig", "jig"))

        for flight in beluga_problem.flights:
            problem.add_object(PDDLParam(flight.name, "beluga"))

        for h in beluga_problem.hanger:
            problem.add_object(PDDLParam(h, "hanger"))

        for pl in beluga_problem.production_lines:
            problem.add_object(PDDLParam(pl.name, "production-line"))


        #### INIT 
        jig_sizes = set([p.size_loaded for p in beluga_problem.jigs] + [p.size_empty for p in beluga_problem.jigs])
        sum_sizes_all_jigs = sum([j.size_loaded for j in beluga_problem.jigs])
        max_num = max([r.size for r in beluga_problem.racks] + [sum_sizes_all_jigs])

        
        if ef.encoding == EncodingOptions.CLASSIC:
            numbers = utils.get_necessary_numbers(jig_sizes, max_num)

            for n in numbers:
                problem.add_object(PDDLParam("n" + utils.format_number(n, max_num), "num"))


            for rack in beluga_problem.racks:
                for n1 in numbers:
                    for n2 in  jig_sizes:
                        if (n1 + n2 <= rack.size):
                            problem.add_init(PDDLPredicate("fit", 
                                " n" + utils.format_number(n1, max_num),
                                " n" + utils.format_number(n2, max_num),
                                " n" + utils.format_number(n1 + n2, max_num),
                                rack.name))
                            
            if ef.beluga == EncodingOptions.BELUGA_RACK:
                for flight in beluga_problem.flights:
                    size_flight = sum([j.size_loaded for j in flight.incoming])
                    for n1 in numbers:
                        for n2 in  jig_sizes:
                            if (n1 + n2 <= size_flight):
                                problem.add_init(PDDLPredicate("fit", 
                                    " n" + utils.format_number(n1, max_num),
                                    " n" + utils.format_number(n2, max_num),
                                    " n" + utils.format_number(n1 + n2, max_num),
                                    flight.name))
                                
            if ef.factory == EncodingOptions.FACTORY_RACK:
                for pl in beluga_problem.production_lines:
                    size_pl = sum([j.size_loaded for j in pl.schedule])
                    for n1 in numbers:
                        for n2 in  jig_sizes:
                            if (n1 + n2 <= size_pl):
                                problem.add_init(PDDLPredicate("fit", 
                                    " n" + utils.format_number(n1, max_num),
                                    " n" + utils.format_number(n2, max_num),
                                    " n" + utils.format_number(n1 + n2, max_num),
                                    pl.name))
                                

        for truck in beluga_problem.trucks_beluga:
            problem.add_init(PDDLPredicate("empty", truck.name));
            problem.add_init(PDDLPredicate("at-side", truck.name, 'bside'))
            if FeatureOptions.DRIVING in ef.feature_options:
                problem.add_init(PDDLPredicate("at-loc", truck.name, beluga_problem.flights[0].name))
        

        for truck in beluga_problem.trucks_factory:
            problem.add_init(PDDLPredicate("empty", truck.name));
            problem.add_init(PDDLPredicate("at-side", truck.name, 'fside'))
            if FeatureOptions.DRIVING in ef.feature_options:
                problem.add_init(PDDLPredicate("at-loc", truck.name, beluga_problem.hanger[0]))


        # distances
        if FeatureOptions.DRIVING in ef.feature_options:
            for i, r1 in enumerate(beluga_problem.racks):
                for j in range(i+1, len(beluga_problem.racks)):
                    r2 = beluga_problem.racks[j]
                    d = abs(i-j) * 2
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + r1.name +  " " + r2.name), PDDLNumericValue(d)))
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + r2.name +  " " + r1.name), PDDLNumericValue(d)))

            for i, r in enumerate(beluga_problem.racks):
                for b in beluga_problem.flights:
                    d = (i + 1) * 2
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + r.name +  " " + b.name), PDDLNumericValue(d)))
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + b.name +  " " + r.name), PDDLNumericValue(d)))

            for i, r in enumerate(beluga_problem.racks):
                for h in beluga_problem.hanger:
                    d = 1
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + r.name +  " " + h), PDDLNumericValue(d)))
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("distance " + h +  " " + r.name), PDDLNumericValue(d)))


        if ef.beluga == EncodingOptions.BELUGA_RACK:
            for flight in beluga_problem.flights:
                problem.add_init(PDDLPredicate("at-side", flight.name, 'bside'))
                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("free-space", flight.name, "n" + utils.format_number(0, max_num)))

                if ef.encoding == EncodingOptions.NUMERIC:
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("free-space " + flight.name), PDDLNumericValue(0))) 


        for h in beluga_problem.hanger:
            problem.add_init(PDDLPredicate("empty", h));



        #RACK
        if  ModelTricks.RACK_RANKING in ef.model_tricks:
            problem.add_init(PDDLPredicate("used", "dummy-rack"))
        for i, rack in enumerate(beluga_problem.racks):
            problem.add_init(PDDLPredicate("empty", rack.name))   
            problem.add_init(PDDLPredicate("at-side", rack.name, 'bside')) 
            problem.add_init(PDDLPredicate("at-side", rack.name, 'fside'))                 
            if ef.encoding == EncodingOptions.CLASSIC:
                problem.add_init(PDDLPredicate("free-space", rack.name, "n" + utils.format_number(rack.size, max_num)))

            if ef.encoding == EncodingOptions.NUMERIC:
                problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("free-space " + rack.name), PDDLNumericValue(rack.size)))    


            if  ModelTricks.RACK_RANKING in ef.model_tricks:
                if i == 0:
                    problem.add_init(PDDLPredicate("use_before", "dummy-rack", rack.name))
                else:
                    problem.add_init(PDDLPredicate("use_before", beluga_problem.racks[i-1].name, rack.name))


        # JIGS
        for jig in beluga_problem.jigs:
            if ef.encoding == EncodingOptions.CLASSIC:
                problem.add_init(PDDLPredicate("size", jig.name, "n" + utils.format_number(jig.size_loaded, max_num)))

            if ef.encoding == EncodingOptions.NUMERIC:
                problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("size " + jig.name), PDDLNumericValue(jig.size_loaded))) 


            if FeatureOptions.OUTGOING_EMPTY_JIGS in ef.feature_options:
                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("empty-size", jig.name, "n" + utils.format_number(jig.size_empty, max_num)))

                if ef.encoding == EncodingOptions.NUMERIC:
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("empty-size " + jig.name), PDDLNumericValue(jig.size_empty)))  


        if FeatureOptions.FLIGHT_SCHEDULE in  ef.feature_options:
            problem.add_init(PDDLPredicate("in-phase", beluga_problem.flights[0].name)) 
                            
        # JIGS INCOMING
        for flight in beluga_problem.flights:
            if ef.beluga == EncodingOptions.BELUGA_SPECIAL:
                if ef.encoding == EncodingOptions.NUMERIC:
                    problem.add_init(PDDLNumericPredicate("=",  PDDLNumericParam("unload-process " + flight.name), PDDLNumericValue(len(flight.incoming))))
                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("to_unload", flight.incoming[0].name, flight.name))
            
            for i, jig in enumerate(flight.incoming):
                problem.add_init(PDDLPredicate("in", jig.name, flight.name))

                if ef.beluga == EncodingOptions.BELUGA_SPECIAL:
                    if ef.encoding == EncodingOptions.CLASSIC:
                        if i < len(flight.incoming) - 1:
                            problem.add_init(PDDLPredicate("next_unload", jig.name, flight.incoming[i+1].name))
                        else:
                            problem.add_init(PDDLPredicate("next_unload", jig.name, 'dummy-jig'))

                    if ef.encoding == EncodingOptions.NUMERIC:
                        problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("unload-order " + jig.name), PDDLNumericValue(len(flight.incoming) - i)))

                if ef.beluga == EncodingOptions.BELUGA_RACK:
                    if i == 0:
                         problem.add_init(PDDLPredicate("clear", jig.name, 'bside'))
                    if i < len(flight.incoming) - 1:
                        problem.add_init(PDDLPredicate("on", jig.name, flight.incoming[i+1].name, 'bside'))
                        problem.add_init(PDDLPredicate("on", flight.incoming[i+1].name, jig.name, 'fside'))
                    if i == len(flight.incoming) - 1:
                         problem.add_init(PDDLPredicate("clear", jig.name, 'fside'))

            if FeatureOptions.FLIGHT_SCHEDULE in  ef.feature_options:
                for i, jig in enumerate(flight.outgoing):
                    problem.add_init(PDDLPredicate("outgoing", jig.name, flight.name))

                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("load-process", flight.name, str(len(flight.incoming))))

            if FeatureOptions.OUTGOING_EMPTY_JIGS in  ef.feature_options:
                if ef.beluga == EncodingOptions.BELUGA_SPECIAL:
                    if ef.encoding == EncodingOptions.CLASSIC:
                            problem.add_init(PDDLPredicate("to_load", flight.outgoing[0].name, flight.name));
                            for i, jig in enumerate(flight.outgoing):
                                if i < len(flight.outgoing) - 1:
                                    problem.add_init(PDDLPredicate("next_load", jig.name, flight.outgoing[i+1].name))
                                else:
                                    problem.add_init(PDDLPredicate("next_load", jig.name, 'dummy-jig'))

                    if ef.encoding == EncodingOptions.NUMERIC:
                        problem.add_init(PDDLNumericPredicate("=",  PDDLNumericParam("load-process " + flight.name), PDDLNumericValue(len(flight.outgoing))))
                        for i, jig in enumerate(flight.outgoing):
                            problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("load-order " + jig.name), PDDLNumericValue(len(flight.outgoing) - i))) 
                    

        #production schedule
        for pl in beluga_problem.production_lines:

            if ef.factory == EncodingOptions.FACTORY_SPECIAL:
                if ef.encoding == EncodingOptions.NUMERIC:
                        problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("delivery-process " + pl.name), PDDLNumericValue(len(pl.schedule))))
                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("to_deliver", pl.schedule[0].name, beluga_problem.flights[0].name));

                for i,jig in enumerate(pl.schedule):
                    if ef.encoding == EncodingOptions.CLASSIC:
                        if i < len(pl.schedule) - 1:
                            problem.add_init(PDDLPredicate("next_deliver", jig.name, pl.schedule[i+1].name))
                        else:
                            problem.add_init(PDDLPredicate("next_deliver", jig.name, 'dummy-jig'))

                    if ef.encoding == EncodingOptions.NUMERIC:
                        problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("delivery-order " + jig.name), PDDLNumericValue(len(pl.schedule) - i)))


        if ef.factory == EncodingOptions.FACTORY_RACK:
            for pl in beluga_problem.production_lines:
                problem.add_init(PDDLPredicate("at-side", pl.name, 'fside'))
                problem.add_init(PDDLPredicate("empty", pl.name))
                if ef.encoding == EncodingOptions.CLASSIC:
                    problem.add_init(PDDLPredicate("free-space", pl.name, "n" + utils.format_number(sum([j.size_loaded for j in pl.schedule]), max_num)))

                if ef.encoding == EncodingOptions.NUMERIC:
                    problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("free-space " + pl.name), PDDLNumericValue(sum([j.size_loaded for j in pl.schedule])))) 


        # total action cost
        problem.add_init(PDDLNumericPredicate("=", PDDLNumericParam("total-cost"), PDDLNumericValue(0)))


        ##### GOAL
        for pl in beluga_problem.production_lines:
            if ef.factory == EncodingOptions.FACTORY_SPECIAL:
                for jig in pl.schedule:
                    problem.add_goal(PDDLPredicate("empty", jig.name))

            if ef.factory == EncodingOptions.FACTORY_RACK:
                for i, jig in enumerate(pl.schedule):
                    problem.add_goal(PDDLPredicate("in", jig.name, pl.name))
                    if i < len(pl.schedule) - 1:
                        problem.add_goal(PDDLPredicate("on", pl.schedule[i+1].name, jig.name, 'fside'))

        if FeatureOptions.OUTGOING_EMPTY_JIGS in  ef.feature_options:
            for flight in beluga_problem.flights:
                for i, jig in enumerate(flight.outgoing):
                    problem.add_goal(PDDLPredicate("in", jig.name, flight.name)) 


        return problem
