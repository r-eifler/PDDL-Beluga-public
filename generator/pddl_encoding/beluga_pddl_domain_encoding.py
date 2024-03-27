from pddl.pddl_action import PDDLAction
from pddl.pddl_domain import PDDLDomain
from pddl.pddl_param import PDDLNumericParam
from pddl.pddl_predicate_def import PDDLPredicateDef
from pddl.type import Type
from pddl import PDDLParam, PDDLNumericPredicate, PDDLNumericValue

from encoding_features import EncodingFeatures, EncodingOptions, FeatureOptions, ModelTricks

class DomainEncoding:

    def __init__(self, encoding_features : EncodingFeatures) -> None:
        self.ef = encoding_features

        self.domain = PDDLDomain();
    
        self.generate_types()
        self.generate_constants()
        self.generate_predicates()
        self.generate_functions()

        if self.ef.beluga == EncodingOptions.BELUGA_SPECIAL:
            self.generate_special_beluga_actions()

        if self.ef.factory == EncodingOptions.FACTORY_SPECIAL:
            self.generate_special_factory_actions()

        # if self.ef.load_encoding == EncodingOptions.LOAD_AND_UNLOAD:
        self.generate_load_unload_rack_actions()

        if FeatureOptions.DRIVING in self.ef.feature_options:
            self.generate_drive_actions()

        if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
            self.generate_beluga_complete()    



    def generate_types(self) -> None:
        self.location: Type = Type('location', 'object')
        self.side: Type = Type('side', 'object')

        self.rack: Type = Type('rack', 'location')

        if self.ef.factory == EncodingOptions.FACTORY_RACK:
            self.production_line: Type = Type('production-line', 'rack')
        if self.ef.factory == EncodingOptions.FACTORY_SPECIAL:
            self.production_line: Type = Type('production-line', 'object')
        self.domain.types += [self.location, self.side, self.rack, self.production_line]

        if self.ef.encoding == EncodingOptions.CLASSIC:
            self.num: Type = Type('num', 'object')
            self.domain.types.append(self.num)

        self.truck: Type = Type('truck', 'location')
        self.jig: Type = Type('jig', 'location')
        self.hanger: Type = Type('hanger', 'location')

        if self.ef.beluga == EncodingOptions.BELUGA_RACK:
            self.beluga: Type = Type('beluga', 'rack')
        if self.ef.beluga == EncodingOptions.BELUGA_SPECIAL:
            self.beluga: Type = Type('beluga', 'location')

        self.domain.types += [self.truck,self.jig,self.hanger,self.beluga]


    def generate_constants(self) -> None:
        self.domain.constants.append(PDDLParam("bside", 'side'))
        self.domain.constants.append(PDDLParam("fside", 'side'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            self.domain.constants.append(PDDLParam("dummy-jig", 'jig'))


    def generate_predicates(self) -> None:
        self.equal = PDDLPredicateDef("=", PDDLParam("?o1", "object"), PDDLParam("?o2", "object"))

        self.inp = PDDLPredicateDef("in", PDDLParam("?j", "jig"), PDDLParam("?l", "location"))
        self.empty = PDDLPredicateDef("empty", PDDLParam("?l", "location"))
        self.at_loc_side = PDDLPredicateDef("at-side", PDDLParam("?l", "location"), PDDLParam("?s", "side"))
        self.domain.predicates += [self.inp,self.empty,self.at_loc_side]

        if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
            self.in_phase = PDDLPredicateDef("in-phase", PDDLParam("?b", "beluga"))
            self.outgoing  = PDDLPredicateDef("outgoing", PDDLParam("?j", "jig"), PDDLParam("?b", "beluga"))
            # self.part_of  = PDDLPredicateDef("part-of", PDDLParam("?j", "jig"), PDDLParam("?pl", "production-line"))
            self.domain.predicates += [self.in_phase, self.outgoing] #, self.part_of]


        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            self.on = PDDLPredicateDef("on", PDDLParam("?j1", "jig"), PDDLParam("?j2", "jig"), PDDLParam("?s", "side"))
            self.clear = PDDLPredicateDef("clear", PDDLParam("?j", "jig"), PDDLParam("?s", "side"))
            self.domain.predicates += [self.on,self.clear]

        if self.ef.rack_encoding == EncodingOptions.RACK_POSITION_POINTER:
            assert False, "Not yet implemented!"
        
        if FeatureOptions.DRIVING in self.ef.feature_options:
            self.at_loc = PDDLPredicateDef("at-loc", PDDLParam("?t", "truck"), PDDLParam("?l", "location"))
            self.domain.predicates += [self.at_loc]

        
        if self.ef.encoding == EncodingOptions.CLASSIC:

            self.size = PDDLPredicateDef("size", PDDLParam("?j", "jig"), PDDLParam("?n", "num"))
            self.free_space = PDDLPredicateDef("free-space", PDDLParam("?r", "rack"), PDDLParam("?n", "num"))
            #n1 + n2 = n3
            self.fit = PDDLPredicateDef("fit", PDDLParam("?n1", "num"), PDDLParam("?n2", "num"), PDDLParam("?n3", "num"), PDDLParam("?r", "rack"))
            self.domain.predicates += [self.size,self.free_space,self.fit]
            
            if FeatureOptions.OUTGOING_EMPTY_JIGS in  self.ef.feature_options:
                self.empty_size = PDDLPredicateDef("empty-size", PDDLParam("?j", "jig"), PDDLParam("?n", "num"))
                self.domain.predicates.append(self.empty_size)


            if self.ef.beluga == EncodingOptions.BELUGA_SPECIAL:
                self.to_unload = PDDLPredicateDef("to_unload", PDDLParam("?j1", "jig"),  PDDLParam("?b", "beluga"))
                self.next_unload = PDDLPredicateDef("next_unload", PDDLParam("?j1", "jig"), PDDLParam("?j2", "jig"))
                self.domain.predicates += [self.to_unload, self.next_unload]

                if FeatureOptions.OUTGOING_EMPTY_JIGS in  self.ef.feature_options:
                    self.to_load = PDDLPredicateDef("to_load", PDDLParam("?j1", "jig"), PDDLParam("?b", "beluga"))
                    self.next_load = PDDLPredicateDef("next_load", PDDLParam("?j1", "jig"), PDDLParam("?j2", "jig"))
                    self.domain.predicates += [self.next_load, self.to_load]

            if self.ef.factory == EncodingOptions.FACTORY_SPECIAL:
                self.to_deliver = PDDLPredicateDef("to_deliver", PDDLParam("?j1", "jig"), PDDLParam("?b", "beluga"))
                self.next_deliver = PDDLPredicateDef("next_deliver", PDDLParam("?j1", "jig"), PDDLParam("?j2", "jig"))
                self.domain.predicates += [self.to_deliver, self.next_deliver]

        if  ModelTricks.RACK_RANKING in self.ef.model_tricks:
            self.used = PDDLPredicateDef("used", PDDLParam("?r", "rack"))
            self.use_before = PDDLPredicateDef("use_before", PDDLParam("?r1", "rack"), PDDLParam("?r2", "rack"))
            self.domain.predicates += [self.used, self.use_before]


    def generate_functions(self) -> None:

        self.total_cost = PDDLPredicateDef("total-cost")
        self.domain.functions.append(self.total_cost)

        if FeatureOptions.DRIVING in  self.ef.feature_options:
            self.distance = PDDLPredicateDef("distance", PDDLParam("?l1", "location"), PDDLParam("?l2", "location"))
            self.domain.functions.append(self.distance)

        if self.ef.encoding == EncodingOptions.NUMERIC:
            self.size = PDDLPredicateDef("size", PDDLParam("?l", "location"))
            self.free_space = PDDLPredicateDef("free-space", PDDLParam("?r", "rack"))
            self.domain.functions += [self.size,self.free_space]

            if self.ef.beluga == EncodingOptions.BELUGA_SPECIAL:
                self.unload_process = PDDLPredicateDef("unload-process", PDDLParam("?b", "beluga"))
                self.unload_order = PDDLPredicateDef("unload-order", PDDLParam("?j", "jig"))
                self.domain.functions += [self.unload_order, self.unload_process]

            if self.ef.factory == EncodingOptions.FACTORY_SPECIAL:
                self.delivery_process = PDDLPredicateDef("delivery-process", PDDLParam("?pl", "production-line"))
                self.delivery_order = PDDLPredicateDef("delivery-order", PDDLParam("?j", "jig"))
                self.domain.functions += [self.delivery_order, self.delivery_process]

            if FeatureOptions.OUTGOING_EMPTY_JIGS in  self.ef.feature_options:
                self.load_order = PDDLPredicateDef("load-order", PDDLParam("?j", "jig"))
                self.load_process = PDDLPredicateDef("load-process", PDDLParam("?b", "beluga"))
                self.empty_size = PDDLPredicateDef("empty-size", PDDLParam("?j", "jig"))
                self.domain.functions += [self.load_order, self.load_process, self.empty_size]

            if FeatureOptions.FLIGHT_SCHEDULE in  self.ef.feature_options:
                self.to_process_parts = PDDLPredicateDef("to-process-parts", PDDLParam("?b", "beluga"))
                self.domain.functions += [self.to_process_parts]

            
    def generate_special_beluga_actions(self) -> None:
        # UNLOAD FROM BELUGA ONTO EMPTY TRUCK
        unload_beluga = PDDLAction('unload-beluga')
        self.domain.actions.append(unload_beluga)

        unload_beluga.add_parameter(PDDLParam('?j', 'jig'))
        unload_beluga.add_parameter(PDDLParam('?b', 'beluga'))
        unload_beluga.add_parameter(PDDLParam('?t', 'truck'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            unload_beluga.add_parameter(PDDLParam('?jn', 'jig'))
            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                unload_beluga.add_parameter(PDDLParam('?jsize', 'num'))
                unload_beluga.add_parameter(PDDLParam('?fspace', 'num'))
                unload_beluga.add_parameter(PDDLParam('?nspace', 'num'))

        unload_beluga.add_precondition(self.inp.gp('?j','?b'))
        unload_beluga.add_precondition(self.empty.gp('?t'))
        unload_beluga.add_precondition(self.at_loc_side.gp('?t', 'bside'))

        if FeatureOptions.DRIVING in self.ef.feature_options:
            unload_beluga.add_precondition(self.at_loc.gp('?t','?b'))

        if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
            unload_beluga.add_precondition(self.in_phase.gp('?b'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            unload_beluga.add_precondition(self.to_unload.gp('?j', '?b'))
            unload_beluga.add_precondition(self.next_unload.gp('?j', '?jn'))
            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                unload_beluga.add_precondition(self.size.gp('?j', '?jSize'))
                unload_beluga.add_precondition(self.free_space.gp('?t', '?fspace'))
                unload_beluga.add_precondition(self.fit.gp('?nspace', '?jsize', '?fspace', '?r'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            unload_beluga.add_precondition(PDDLNumericPredicate('=', self.unload_order.gp('?j'), self.unload_process.gp('?b')))
            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                unload_beluga.add_precondition(PDDLNumericPredicate('>=', 
                    PDDLNumericPredicate("-", self.free_space.gp('?t'), self.size.gp('?t')), 
                    PDDLNumericValue(0)))


        unload_beluga.add_effect(self.inp.gp_neg('?j','?b'))
        unload_beluga.add_effect(self.inp.gp('?j','?t'))
        unload_beluga.add_effect(self.empty.gp_neg('?t'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            unload_beluga.add_effect(self.to_unload.gp_neg('?j', '?b'))
            unload_beluga.add_effect(self.to_unload.gp('?jn', '?b'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            unload_beluga.add_effect(PDDLNumericPredicate('decrease', self.unload_process.gp('?b'), PDDLNumericValue(1)))

        if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
            if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
                unload_beluga.add_effect(self.clear.gp('?j','bside'))
                unload_beluga.add_effect(self.clear.gp('?j','fside'))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                unload_beluga.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                unload_beluga.add_effect(self.free_space.gp('?t', '?nspace'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                unload_beluga.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?t'), self.size.gp('?j')))

        unload_beluga.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        # UNLOAD FROM BELUGA ONTO ALREADY LOADED TRUCK
        if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
            unload_tc_beluga = PDDLAction('unload-tc-beluga')
            self.domain.actions.append(unload_tc_beluga)

            unload_tc_beluga.add_parameter(PDDLParam('?j', 'jig'))
            unload_tc_beluga.add_parameter(PDDLParam('?njt', 'jig'))
            unload_tc_beluga.add_parameter(PDDLParam('?b', 'beluga'))
            unload_tc_beluga.add_parameter(PDDLParam('?t', 'truck'))
            unload_tc_beluga.add_parameter(PDDLParam('?s', 'side'))
            unload_tc_beluga.add_parameter(PDDLParam('?os', 'side'))
            if self.ef.encoding == EncodingOptions.CLASSIC:
                unload_beluga.add_parameter(PDDLParam('?njb', 'jig'))
                if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                    unload_tc_beluga.add_parameter(PDDLParam('?jsize', 'num'))
                    unload_tc_beluga.add_parameter(PDDLParam('?fspace', 'num'))
                    unload_tc_beluga.add_parameter(PDDLParam('?nspace', 'num'))

            unload_tc_beluga.add_precondition(self.equal.gp_neg('?j','?njt'))
            unload_tc_beluga.add_precondition(self.equal.gp_neg('?s','?os'))

            unload_tc_beluga.add_precondition(self.inp.gp('?j','?b'))
            unload_tc_beluga.add_precondition(self.inp.gp('?njt','?t'))
            unload_tc_beluga.add_precondition(self.clear.gp('?njt','?s'))
            unload_tc_beluga.add_precondition(self.at_loc_side.gp('?t', 'bside'))

            if FeatureOptions.DRIVING in self.ef.feature_options:
                unload_tc_beluga.add_precondition(self.at_loc.gp('?t','?b'))

            if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
                unload_tc_beluga.add_precondition(self.in_phase.gp('?b'))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                unload_tc_beluga.add_precondition(self.to_unload.gp('?j', '?b'))
                unload_tc_beluga.add_precondition(self.next_unload.gp('?j', '?jnb'))
                unload_tc_beluga.add_precondition(self.size.gp('?j', '?jSize'))
                unload_tc_beluga.add_precondition(self.free_space.gp('?t', '?fspace'))
                unload_tc_beluga.add_precondition(self.fit.gp('?nspace', '?jsize', '?fspace', '?r'))

            if self.ef.encoding == EncodingOptions.NUMERIC:
                unload_tc_beluga.add_precondition(PDDLNumericPredicate('=', self.unload_order.gp('?j'), self.unload_process.gp('?b')))
                unload_tc_beluga.add_precondition(PDDLNumericPredicate('>=', 
                    PDDLNumericPredicate("-", self.free_space.gp('?t'), self.size.gp('?t')), 
                    PDDLNumericValue(0)))


            unload_tc_beluga.add_effect(self.inp.gp_neg('?j','?b'))
            unload_tc_beluga.add_effect(self.inp.gp('?j','?t'))

            unload_tc_beluga.add_effect(self.clear.gp_neg('?njt','?s'))
            unload_tc_beluga.add_effect(self.clear.gp('?j','?s'))
            unload_tc_beluga.add_effect(self.on.gp('?j','?njt','?s'))
            unload_tc_beluga.add_effect(self.on.gp('?nj','?jt','?os'))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                unload_tc_beluga.add_effect(self.to_unload.gp_neg('?j', '?b'))
                unload_tc_beluga.add_effect(self.to_unload.gp('?njb', '?b'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                unload_tc_beluga.add_effect(PDDLNumericPredicate('decrease', self.unload_process.gp('?b'), PDDLNumericValue(1)))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                unload_tc_beluga.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                unload_tc_beluga.add_effect(self.free_space.gp('?t', '?nspace'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                unload_tc_beluga.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?t'), self.size.gp('?j')))

            unload_tc_beluga.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        # LOAD INTO BELUGA
        if FeatureOptions.OUTGOING_EMPTY_JIGS in  self.ef.feature_options:
            load_beluga = PDDLAction('load-beluga')
            self.domain.actions.append(load_beluga)

            load_beluga.add_parameter(PDDLParam('?j', 'jig'))
            load_beluga.add_parameter(PDDLParam('?b', 'beluga'))
            load_beluga.add_parameter(PDDLParam('?t', 'truck'))
            if self.ef.encoding == EncodingOptions.CLASSIC:
                load_beluga.add_parameter(PDDLParam('?jn', 'jig'))

            load_beluga.add_precondition(self.inp.gp('?j','?t'))
            load_beluga.add_precondition(self.empty.gp('?j'))
            load_beluga.add_precondition(self.at_loc_side.gp('?t', 'bside'))

            if FeatureOptions.DRIVING in self.ef.feature_options:
                load_beluga.add_precondition(self.at_loc.gp('?t','?b'))

            if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
                load_beluga.add_precondition(self.in_phase.gp('?b'))
                load_beluga.add_precondition(self.outgoing.gp('?j', '?b'))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                load_beluga.add_precondition(self.to_load.gp('?j', '?b'))
                load_beluga.add_precondition(self.next_load.gp('?j', '?jn'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                load_beluga.add_precondition(PDDLNumericPredicate('=', self.load_order.gp('?j'), self.load_process.gp('?b')))


            load_beluga.add_effect(self.inp.gp('?j','?b'))
            load_beluga.add_effect(self.inp.gp_neg('?j','?t'))
            load_beluga.add_effect(self.empty.gp('?t'))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                load_beluga.add_effect(self.to_load.gp_neg('?j', '?b'))
                load_beluga.add_effect(self.to_load.gp('?jn', '?b'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                load_beluga.add_effect(PDDLNumericPredicate('decrease', self.load_process.gp('?b'), PDDLNumericValue(1)))

            load_beluga.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))

            # LOAD INTO BELUGA with remaining jigs on truck
            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                load_tc_beluga = PDDLAction('load-tc-beluga')
                self.domain.actions.append(load_tc_beluga)

                load_tc_beluga.add_parameter(PDDLParam('?j', 'jig'))
                load_tc_beluga.add_parameter(PDDLParam('?b', 'beluga'))
                load_tc_beluga.add_parameter(PDDLParam('?t', 'truck'))
                load_tc_beluga.add_parameter(PDDLParam('?njt', 'jig'))
                load_tc_beluga.add_parameter(PDDLParam('?s', 'side'))
                load_tc_beluga.add_parameter(PDDLParam('?os', 'side'))
                if self.ef.encoding == EncodingOptions.CLASSIC:
                    load_tc_beluga.add_parameter(PDDLParam('?njb', 'jig'))

                load_tc_beluga.add_precondition(self.equal.gp_neg('?j','?njt'))
                load_tc_beluga.add_precondition(self.equal.gp_neg('?s','?os'))

                load_tc_beluga.add_precondition(self.inp.gp('?j','?t'))
                load_tc_beluga.add_precondition(self.inp.gp('?njt','?t'))
                load_tc_beluga.add_precondition(self.empty.gp('?j'))
                load_tc_beluga.add_precondition(self.at_loc_side.gp('?t', 'bside'))

                load_tc_beluga.add_precondition(self.clear.gp('?j', '?s'))
                load_tc_beluga.add_precondition(self.on.gp('?j', '?njt', '?s'))
                load_tc_beluga.add_precondition(self.on.gp('?njt', '?j', '?os'))

                if FeatureOptions.DRIVING in self.ef.feature_options:
                    load_tc_beluga.add_precondition(self.at_loc.gp('?t','?b'))

                if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
                    load_tc_beluga.add_precondition(self.in_phase.gp('?b'))
                    load_tc_beluga.add_precondition(self.outgoing.gp('?j', '?b'))

                if self.ef.encoding == EncodingOptions.CLASSIC:
                    load_tc_beluga.add_precondition(self.to_load.gp('?j', '?b'))
                    load_tc_beluga.add_precondition(self.next_load.gp('?j', '?njb'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    load_tc_beluga.add_precondition(PDDLNumericPredicate('=', self.load_order.gp('?j'), self.load_process.gp('?b')))


                load_tc_beluga.add_effect(self.inp.gp('?j','?b'))
                load_tc_beluga.add_effect(self.inp.gp_neg('?j','?t'))
                
                load_tc_beluga.add_effect(self.clear.gp('?njt', '?s'))
                load_tc_beluga.add_effect(self.on.gp_neg('?j', '?njt', '?s'))
                load_tc_beluga.add_effect(self.on.gp_neg('?njt', '?j', '?os'))


                if self.ef.encoding == EncodingOptions.CLASSIC:
                    load_tc_beluga.add_effect(self.to_load.gp_neg('?j', '?b'))
                    load_tc_beluga.add_effect(self.to_load.gp('?njb', '?b'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    load_tc_beluga.add_effect(PDDLNumericPredicate('decrease', self.load_process.gp('?b'), PDDLNumericValue(1)))
                    load_tc_beluga.add_effect(PDDLNumericPredicate('increase', self.free_space.gp('?t'), self.size.gp('?j')))

                load_tc_beluga.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


    def generate_special_factory_actions(self) -> None:
        if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
            get_from_hanger = PDDLAction('get-from-hanger')
            self.domain.actions.append(get_from_hanger)

            get_from_hanger.add_parameter(PDDLParam('?j', 'jig'))
            get_from_hanger.add_parameter(PDDLParam('?t', 'truck'))
            get_from_hanger.add_parameter(PDDLParam('?h', 'hanger'))

            get_from_hanger.add_precondition(self.inp.gp('?j','?h'))
            get_from_hanger.add_precondition(self.empty.gp('?t'))
            get_from_hanger.add_precondition(self.at_loc_side.gp('?t', 'fside'))

            if FeatureOptions.DRIVING in self.ef.feature_options:
                get_from_hanger.add_precondition(self.at_loc.gp('?t','?h'))

            get_from_hanger.add_effect(self.inp.gp_neg('?j','?h'))
            get_from_hanger.add_effect(self.inp.gp('?j','?t'))
            get_from_hanger.add_effect(self.empty.gp_neg('?t'))
            get_from_hanger.add_effect(self.empty.gp('?h'))

            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                get_from_hanger.add_effect(self.clear.gp('?j','bside'))
                get_from_hanger.add_effect(self.clear.gp('?j','fside'))

                if self.ef.encoding == EncodingOptions.CLASSIC:
                    get_from_hanger.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                    get_from_hanger.add_effect(self.free_space.gp('?t', '?nspace'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    get_from_hanger.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?t'), self.size.gp('?t')))

            get_from_hanger.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                get_from_hanger_tc = PDDLAction('get-from-hanger-tc')
                self.domain.actions.append(get_from_hanger_tc)

                get_from_hanger_tc.add_parameter(PDDLParam('?j', 'jig'))
                get_from_hanger_tc.add_parameter(PDDLParam('?nj', 'jig'))
                get_from_hanger_tc.add_parameter(PDDLParam('?t', 'truck'))
                get_from_hanger_tc.add_parameter(PDDLParam('?h', 'hanger'))
                get_from_hanger_tc.add_parameter(PDDLParam('?s', 'side'))
                get_from_hanger_tc.add_parameter(PDDLParam('?os', 'side'))

                get_from_hanger_tc.add_precondition(self.equal.gp_neg('?j','?nj'))
                get_from_hanger_tc.add_precondition(self.equal.gp_neg('?s','?os'))
                get_from_hanger_tc.add_precondition(self.inp.gp('?j','?h'))
                get_from_hanger_tc.add_precondition(self.inp.gp('?nj','?t'))
                get_from_hanger_tc.add_precondition(self.at_loc_side.gp('?t', 'fside'))
                get_from_hanger_tc.add_precondition(self.clear.gp('?nj','?s'))

                if FeatureOptions.DRIVING in self.ef.feature_options:
                    get_from_hanger_tc.add_precondition(self.at_loc.gp('?t','?h'))

                get_from_hanger_tc.add_precondition(PDDLNumericPredicate('>=', 
                    PDDLNumericPredicate("-", self.free_space.gp('?t'), self.size.gp('?j')), 
                    PDDLNumericValue(0)))

                get_from_hanger_tc.add_effect(self.inp.gp_neg('?j','?h'))
                get_from_hanger_tc.add_effect(self.inp.gp('?j','?t'))
                get_from_hanger_tc.add_effect(self.empty.gp('?h'))

                get_from_hanger_tc.add_effect(self.clear.gp('?j','?s'))
                get_from_hanger_tc.add_effect(self.clear.gp_neg('?nj','?s'))
                get_from_hanger_tc.add_effect(self.on.gp('?j','?nj','?s'))
                get_from_hanger_tc.add_effect(self.on.gp('?nj','?j','?os'))
                

                if self.ef.encoding == EncodingOptions.CLASSIC:
                    get_from_hanger_tc.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                    get_from_hanger_tc.add_effect(self.free_space.gp('?t', '?nspace'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    get_from_hanger_tc.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?t'), self.size.gp('?t')))

                get_from_hanger_tc.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        deliver_to_hanger = PDDLAction('deliver-to-hanger')
        self.domain.actions.append(deliver_to_hanger)

        deliver_to_hanger.add_parameter(PDDLParam('?j', 'jig'))
        deliver_to_hanger.add_parameter(PDDLParam('?h', 'hanger'))
        deliver_to_hanger.add_parameter(PDDLParam('?b', 'beluga'))
        deliver_to_hanger.add_parameter(PDDLParam('?t', 'truck'))
        deliver_to_hanger.add_parameter(PDDLParam('?pl', 'production-line'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            deliver_to_hanger.add_parameter(PDDLParam('?jn', 'jig'))
            if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
                deliver_to_hanger.add_parameter(PDDLParam('?s', 'num'))
                deliver_to_hanger.add_parameter(PDDLParam('?es', 'num'))

        deliver_to_hanger.add_precondition(self.inp.gp('?j','?t'))
        deliver_to_hanger.add_precondition(self.empty.gp('?h'))
        deliver_to_hanger.add_precondition(self.at_loc_side.gp('?t', 'fside'))
        
        if FeatureOptions.DRIVING in self.ef.feature_options:
            deliver_to_hanger.add_precondition(self.at_loc.gp('?t','?h'))

        if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
            deliver_to_hanger.add_precondition(self.in_phase.gp('?b'))
            # deliver_to_hanger.add_precondition(self.part_of.gp('?j', '?pl'))

        if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
            deliver_to_hanger.add_precondition(self.clear.gp('?j','bside'))
            deliver_to_hanger.add_precondition(self.clear.gp('?j','fside'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            deliver_to_hanger.add_precondition(self.to_deliver.gp('?j', '?b'))
            deliver_to_hanger.add_precondition(self.next_deliver.gp('?j', '?jn'))
            if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
                deliver_to_hanger.add_precondition(self.size.gp('?j', '?s'))
                deliver_to_hanger.add_precondition(self.empty_size.gp('?j', '?es'))

        if self.ef.encoding == EncodingOptions.NUMERIC:
            deliver_to_hanger.add_precondition(PDDLNumericPredicate('=', self.delivery_order.gp('?j'), self.delivery_process.gp('?pl')))


        deliver_to_hanger.add_effect(self.empty.gp('?t'))
        deliver_to_hanger.add_effect(self.empty.gp('?j'))

        if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
            deliver_to_hanger.add_effect(self.clear.gp_neg('?j','bside'))
            deliver_to_hanger.add_effect(self.clear.gp_neg('?j','fside'))
            if self.ef.encoding == EncodingOptions.CLASSIC:
                deliver_to_hanger.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                deliver_to_hanger.add_effect(self.free_space.gp('?t', '?nspace'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                deliver_to_hanger.add_effect(PDDLNumericPredicate('increase', self.free_space.gp('?t'), self.size.gp('?t')))

        if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
            deliver_to_hanger.add_effect(self.empty.gp_neg('?h'))
            deliver_to_hanger.add_effect(self.inp.gp('?j','?h'))
            deliver_to_hanger.add_effect(self.inp.gp_neg('?j','?t'))
            if self.ef.encoding == EncodingOptions.CLASSIC:
                deliver_to_hanger.add_effect(self.size.gp_neg('?j', '?s'))
                deliver_to_hanger.add_effect(self.size.gp('?j', '?es'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                deliver_to_hanger.add_effect(PDDLNumericPredicate('assign', self.size.gp('?j'), self.empty_size.gp('?j')))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            deliver_to_hanger.add_effect(self.to_deliver.gp_neg('?j', '?b'))
            deliver_to_hanger.add_effect(self.to_deliver.gp('?jn', '?b'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            deliver_to_hanger.add_effect(PDDLNumericPredicate('decrease', self.delivery_process.gp('?pl'), PDDLNumericValue(1)))

        deliver_to_hanger.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
            deliver_to_hanger_tc = PDDLAction('deliver-to-hanger-tc')
            self.domain.actions.append(deliver_to_hanger_tc)

            deliver_to_hanger_tc.add_parameter(PDDLParam('?j', 'jig'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?nj', 'jig'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?h', 'hanger'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?b', 'beluga'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?t', 'truck'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?pl', 'production-line'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?s', 'side'))
            deliver_to_hanger_tc.add_parameter(PDDLParam('?os', 'side'))
            if self.ef.encoding == EncodingOptions.CLASSIC:
                deliver_to_hanger_tc.add_parameter(PDDLParam('?jn', 'jig'))
                if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
                    deliver_to_hanger_tc.add_parameter(PDDLParam('?s', 'num'))
                    deliver_to_hanger_tc.add_parameter(PDDLParam('?es', 'num'))

            deliver_to_hanger_tc.add_precondition(self.inp.gp('?j','?t'))
            deliver_to_hanger_tc.add_precondition(self.inp.gp('?nj','?t'))
            deliver_to_hanger_tc.add_precondition(self.empty.gp('?h'))
            deliver_to_hanger_tc.add_precondition(self.at_loc_side.gp('?t', 'fside'))
            deliver_to_hanger_tc.add_precondition(self.clear.gp('?j','?s'))
            deliver_to_hanger_tc.add_precondition(self.on.gp('?j', '?nj', '?s'))
            deliver_to_hanger_tc.add_precondition(self.on.gp('?nj', '?j', '?os'))
            
            if FeatureOptions.DRIVING in self.ef.feature_options:
                deliver_to_hanger_tc.add_precondition(self.at_loc.gp('?t','?h'))

            if FeatureOptions.FLIGHT_SCHEDULE in self.ef.feature_options:
                deliver_to_hanger_tc.add_precondition(self.in_phase.gp('?b'))
                # deliver_to_hanger_tc.add_precondition(self.part_of.gp('?j', '?pl'))

            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                deliver_to_hanger_tc.add_precondition(self.clear.gp('?j','bside'))
                deliver_to_hanger_tc.add_precondition(self.clear.gp('?j','fside'))
    
            if self.ef.encoding == EncodingOptions.CLASSIC:
                deliver_to_hanger_tc.add_precondition(self.to_deliver.gp('?j', '?b'))
                deliver_to_hanger_tc.add_precondition(self.next_deliver.gp('?j', '?jn'))
                if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
                    deliver_to_hanger_tc.add_precondition(self.size.gp('?j', '?s'))
                    deliver_to_hanger_tc.add_precondition(self.empty_size.gp('?j', '?es'))

            if self.ef.encoding == EncodingOptions.NUMERIC:
                deliver_to_hanger_tc.add_precondition(PDDLNumericPredicate('=', self.delivery_order.gp('?j'), self.delivery_process.gp('?pl')))


            deliver_to_hanger_tc.add_effect(self.empty.gp('?j'))

            if FeatureOptions.TRUCK_CAPACITY in self.ef.feature_options:
                deliver_to_hanger_tc.add_effect(self.clear.gp_neg('?j','bside'))
                deliver_to_hanger_tc.add_effect(self.clear.gp_neg('?j','fside'))
                deliver_to_hanger_tc.add_effect(self.clear.gp('?nj','?s'))
                deliver_to_hanger_tc.add_effect(self.on.gp_neg('?j', '?nj', '?s'))
                deliver_to_hanger_tc.add_effect(self.on.gp_neg('?nj', '?j', '?os'))
                if self.ef.encoding == EncodingOptions.CLASSIC:
                    deliver_to_hanger_tc.add_effect(self.free_space.gp_neg('?t', '?fspace'))
                    deliver_to_hanger_tc.add_effect(self.free_space.gp('?t', '?nspace'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    deliver_to_hanger_tc.add_effect(PDDLNumericPredicate('increase', self.free_space.gp('?t'), self.size.gp('?t')))

            if FeatureOptions.OUTGOING_EMPTY_JIGS in self.ef.feature_options:
                deliver_to_hanger_tc.add_effect(self.empty.gp_neg('?h'))
                deliver_to_hanger_tc.add_effect(self.inp.gp('?j','?h'))
                deliver_to_hanger_tc.add_effect(self.inp.gp_neg('?j','?t'))
                if self.ef.encoding == EncodingOptions.CLASSIC:
                    deliver_to_hanger_tc.add_effect(self.size.gp_neg('?j', '?s'))
                    deliver_to_hanger_tc.add_effect(self.size.gp('?j', '?es'))
                if self.ef.encoding == EncodingOptions.NUMERIC:
                    deliver_to_hanger_tc.add_effect(PDDLNumericPredicate('assign', self.size.gp('?j'), self.empty_size.gp('?j')))

            if self.ef.encoding == EncodingOptions.CLASSIC:
                deliver_to_hanger_tc.add_effect(self.to_deliver.gp_neg('?j', '?b'))
                deliver_to_hanger_tc.add_effect(self.to_deliver.gp('?jn', '?b'))
            if self.ef.encoding == EncodingOptions.NUMERIC:
                deliver_to_hanger_tc.add_effect(PDDLNumericPredicate('decrease', self.delivery_process.gp('?pl'), PDDLNumericValue(1)))

            deliver_to_hanger_tc.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


    def generate_load_unload_rack_actions(self) -> None:

        # PUT-DOWN ONTO RACK
        put_down = PDDLAction('put-down-rack')
        self.domain.actions.append(put_down)

        put_down.add_parameter(PDDLParam('?j', 'jig'))
        put_down.add_parameter(PDDLParam('?t', 'truck'))
        put_down.add_parameter(PDDLParam('?r', 'rack'))
        put_down.add_parameter(PDDLParam('?s', 'side'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            put_down.add_parameter(PDDLParam('?jsize', 'num'))
            put_down.add_parameter(PDDLParam('?fspace', 'num'))
            put_down.add_parameter(PDDLParam('?nspace', 'num'))
        if  ModelTricks.RACK_RANKING in self.ef.model_tricks:
            put_down.add_parameter(PDDLParam('?rb', 'rack'))

        put_down.add_precondition(self.inp.gp('?j','?t'))
        put_down.add_precondition(self.empty.gp('?r'))
        put_down.add_precondition(self.at_loc_side.gp('?t', '?s'))
        put_down.add_precondition(self.at_loc_side.gp('?r', '?s'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            put_down.add_precondition(self.size.gp('?j', '?jSize'))
            put_down.add_precondition(self.free_space.gp('?r', '?fspace'))
            put_down.add_precondition(self.fit.gp('?nspace', '?jsize', '?fspace', '?r'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            put_down.add_precondition(PDDLNumericPredicate('>=', 
                    PDDLNumericPredicate("-", self.free_space.gp('?r'), self.size.gp('?j')), 
                    PDDLNumericValue(0)))
            
        if FeatureOptions.DRIVING in self.ef.feature_options:
            put_down.add_precondition(self.at_loc.gp('?t','?r'))  

        if  ModelTricks.RACK_RANKING in self.ef.model_tricks:
            put_down.add_precondition(self.used.gp('?rb'))  
            put_down.add_precondition(self.use_before.gp('?rb', '?r'))  

        put_down.add_effect(self.inp.gp('?j','?r'))
        put_down.add_effect(self.inp.gp_neg('?j','?t'))
        put_down.add_effect(self.empty.gp('?t'))
        put_down.add_effect(self.empty.gp_neg('?r'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            put_down.add_effect(self.clear.gp('?j','bside'))
            put_down.add_effect(self.clear.gp('?j','fside'))


        if self.ef.encoding == EncodingOptions.CLASSIC:
            put_down.add_effect(self.free_space.gp_neg('?r', '?fspace'))
            put_down.add_effect(self.free_space.gp('?r', '?nspace'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            put_down.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?r'), self.size.gp('?j')))

        if  ModelTricks.RACK_RANKING in self.ef.model_tricks:
            put_down.add_effect(self.used.gp('?r'))  

        put_down.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        # STACK ONTO RACK
        stack = PDDLAction('stack-rack')
        self.domain.actions.append(stack)

        stack.add_parameter(PDDLParam('?j', 'jig'))
        stack.add_parameter(PDDLParam('?nj', 'jig'))
        stack.add_parameter(PDDLParam('?t', 'truck'))
        stack.add_parameter(PDDLParam('?r', 'rack'))
        stack.add_parameter(PDDLParam('?s', 'side'))
        stack.add_parameter(PDDLParam('?os', 'side'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            stack.add_parameter(PDDLParam('?jsize', 'num'))
            stack.add_parameter(PDDLParam('?fspace', 'num'))
            stack.add_parameter(PDDLParam('?nspace', 'num'))

        stack.add_precondition(self.equal.gp_neg('?s','?os'))
        stack.add_precondition(self.equal.gp_neg('?j','?nj'))
        stack.add_precondition(self.inp.gp('?j','?t'))
        stack.add_precondition(self.inp.gp('?nj','?r'))
        stack.add_precondition(self.at_loc_side.gp('?t', '?s'))
        stack.add_precondition(self.at_loc_side.gp('?r', '?s'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            stack.add_precondition(self.clear.gp('?nj', '?s'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            stack.add_precondition(self.size.gp('?j', '?jSize'))
            stack.add_precondition(self.free_space.gp('?r', '?fspace'))
            stack.add_precondition(self.fit.gp('?nspace', '?jsize', '?fspace', '?r'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            stack.add_precondition(PDDLNumericPredicate('>=', 
                    PDDLNumericPredicate("-", self.free_space.gp('?r'), self.size.gp('?j')), 
                    PDDLNumericValue(0)))
            
        if FeatureOptions.DRIVING in self.ef.feature_options:
            stack.add_precondition(self.at_loc.gp('?t','?r'))

        stack.add_effect(self.inp.gp('?j','?r'))
        stack.add_effect(self.inp.gp_neg('?j','?t'))
        stack.add_effect(self.empty.gp('?t'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            stack.add_effect(self.clear.gp_neg('?nj','?s'))
            stack.add_effect(self.clear.gp('?j','?s'))
            stack.add_effect(self.on.gp('?j','?nj','?s'))
            stack.add_effect(self.on.gp('?nj','?j','?os'))
        

        if self.ef.encoding == EncodingOptions.CLASSIC:
            stack.add_effect(self.free_space.gp_neg('?r', '?fspace'))
            stack.add_effect(self.free_space.gp('?r', '?nspace'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            stack.add_effect(PDDLNumericPredicate('decrease', self.free_space.gp('?r'), self.size.gp('?j')))

        stack.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        # PICK-UP FROM RACK
        pick_up = PDDLAction('pick-up-rack')
        self.domain.actions.append(pick_up)

        pick_up.add_parameter(PDDLParam('?j', 'jig'))
        pick_up.add_parameter(PDDLParam('?t', 'truck'))
        pick_up.add_parameter(PDDLParam('?r', 'rack'))
        pick_up.add_parameter(PDDLParam('?s', 'side'))
        pick_up.add_parameter(PDDLParam('?so', 'side'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            pick_up.add_parameter(PDDLParam('?jsize', 'num'))
            pick_up.add_parameter(PDDLParam('?fspace', 'num'))
            pick_up.add_parameter(PDDLParam('?nspace', 'num'))

        pick_up.add_precondition(self.equal.gp_neg('?s','?so'))
        pick_up.add_precondition(self.empty.gp('?t'))
        pick_up.add_precondition(self.inp.gp('?j','?r'))
        pick_up.add_precondition(self.at_loc_side.gp('?t', '?s'))
        pick_up.add_precondition(self.at_loc_side.gp('?r', '?s'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            pick_up.add_precondition(self.clear.gp('?j','bside'))
            pick_up.add_precondition(self.clear.gp('?j','fside'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            pick_up.add_precondition(self.size.gp('?j', '?jSize'))
            pick_up.add_precondition(self.free_space.gp('?r', '?fspace'))
            pick_up.add_precondition(self.fit.gp('?fspace', '?jsize', '?nspace', '?r'))

        if FeatureOptions.DRIVING in self.ef.feature_options:
            pick_up.add_precondition(self.at_loc.gp('?t','?r'))


        pick_up.add_effect(self.inp.gp('?j','?t'))
        pick_up.add_effect(self.inp.gp_neg('?j','?r'))
        pick_up.add_effect(self.empty.gp('?r'))
        pick_up.add_effect(self.empty.gp_neg('?t'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            pick_up.add_effect(self.clear.gp_neg('?j','bside'))
            pick_up.add_effect(self.clear.gp_neg('?j','fside'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            pick_up.add_effect(self.free_space.gp_neg('?r', '?nspace'))
            pick_up.add_effect(self.free_space.gp('?r', '?fspace'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            pick_up.add_effect(PDDLNumericPredicate('increase', self.free_space.gp('?r'), self.size.gp('?j')))

        if  ModelTricks.RACK_RANKING in self.ef.model_tricks:
            pick_up.add_effect(self.used.gp_neg('?r'))  

        pick_up.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


        # UNSTACK FROM RACK
        unstack = PDDLAction('unstack-rack')
        self.domain.actions.append(unstack)

        unstack.add_parameter(PDDLParam('?j', 'jig'))
        unstack.add_parameter(PDDLParam('?nj', 'jig'))
        unstack.add_parameter(PDDLParam('?t', 'truck'))
        unstack.add_parameter(PDDLParam('?r', 'rack'))
        unstack.add_parameter(PDDLParam('?s', 'side'))
        unstack.add_parameter(PDDLParam('?os', 'side'))
        if self.ef.encoding == EncodingOptions.CLASSIC:
            unstack.add_parameter(PDDLParam('?jsize', 'num'))
            unstack.add_parameter(PDDLParam('?fspace', 'num'))
            unstack.add_parameter(PDDLParam('?nspace', 'num'))

        unstack.add_precondition(self.equal.gp_neg('?s','?os'))
        unstack.add_precondition(self.equal.gp_neg('?j','?nj'))
        unstack.add_precondition(self.empty.gp('?t'))
        unstack.add_precondition(self.inp.gp('?j','?r'))
        unstack.add_precondition(self.inp.gp('?nj','?r'))
        unstack.add_precondition(self.at_loc_side.gp('?t', '?s'))
        unstack.add_precondition(self.at_loc_side.gp('?r', '?s'))        

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            unstack.add_precondition(self.clear.gp('?j','?s'))
            unstack.add_precondition(self.on.gp('?j','?nj','?s'))
            unstack.add_precondition(self.on.gp('?nj','?j','?os'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            unstack.add_precondition(self.size.gp('?j', '?jSize'))
            unstack.add_precondition(self.free_space.gp('?r', '?fspace'))
            unstack.add_precondition(self.fit.gp('?fspace', '?jsize', '?nspace', '?r'))

        if FeatureOptions.DRIVING in self.ef.feature_options:
            unstack.add_precondition(self.at_loc.gp('?t','?r'))


        unstack.add_effect(self.inp.gp('?j','?t'))
        unstack.add_effect(self.inp.gp_neg('?j','?r'))
        unstack.add_effect(self.empty.gp_neg('?t'))

        if self.ef.rack_encoding == EncodingOptions.RACK_LINKED_LIST:
            unstack.add_effect(self.on.gp_neg('?j','?nj','?s'))
            unstack.add_effect(self.on.gp_neg('?nj','?j','?os'))
            unstack.add_effect(self.clear.gp('?nj','?s'))
            unstack.add_effect(self.clear.gp_neg('?j','fside'))
            unstack.add_effect(self.clear.gp_neg('?j','bside'))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            unstack.add_effect(self.free_space.gp_neg('?r', '?nspace'))
            unstack.add_effect(self.free_space.gp('?r', '?fspace'))
        if self.ef.encoding == EncodingOptions.NUMERIC:
            unstack.add_effect(PDDLNumericPredicate('increase', self.free_space.gp('?r'), self.size.gp('?j')))

        unstack.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))


    def generate_drive_actions(self) -> None:

        drive = PDDLAction('drive')
        self.domain.actions.append(drive)

        drive.add_parameter(PDDLParam('?t', 'truck'))
        drive.add_parameter(PDDLParam('?l1', 'location'))
        drive.add_parameter(PDDLParam('?l2', 'location'))

        drive.add_precondition(self.at_loc.gp('?t','?l1'))
    
        drive.add_effect(self.at_loc.gp('?t','?l2'))
        drive.add_effect(self.at_loc.gp_neg('?t','?l1'))

        drive.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), self.distance.gp('?l1', '?l2')))


    def generate_beluga_complete(self) -> None:

        complete = PDDLAction('beluga-complete')
        self.domain.actions.append(complete)

        complete.add_parameter(PDDLParam('?b', 'beluga'))
        complete.add_parameter(PDDLParam('?nb', 'beluga'))

        complete.add_precondition(self.in_phase.gp('?b'))

        if self.ef.encoding == EncodingOptions.NUMERIC:
            # complete.add_precondition(PDDLNumericPredicate('<=', self.to_process_parts.gp('?b'), PDDLNumericParam(0)))
            complete.add_precondition(PDDLNumericPredicate('=', self.unload_process.gp('?b'), PDDLNumericValue(0)))
            complete.add_precondition(PDDLNumericPredicate('=', self.load_process.gp('?b'), PDDLNumericValue(0)))

        if self.ef.encoding == EncodingOptions.CLASSIC:
            complete.add_precondition(self.to_unload.gp('dummy-jig', '?b'))
            complete.add_precondition(self.to_load.gp('dummy-jig', '?b'))
            # complete.add_precondition(self.to_deliver.gp('dummy-jig', '?b')) 
            # TODO enforce a partial delivery the jigs before the next flight


        complete.add_effect(self.in_phase.gp('?nb'))
        complete.add_effect(PDDLNumericPredicate('increase', self.total_cost.gp(), PDDLNumericValue(1)))



