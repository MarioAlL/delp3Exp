import sys
import copy
from progress.bar import IncrementalBar
from consultDeLP import *
from bn import *
from utilsExp import *
import time
import argparse

class Sampling:
    def __init__(self, model_path: str, em_path: str, em_name: str, 
                                                            path_output: str):
        model = read_json_file(model_path)
        self.model = model["af"]
        self.em_var = model["em_var"]
        self.am_rules = len(model["af"])
        self.literals_to_consult = set(model["literals"])
        self.em = BayesNetwork(em_name, em_path)
        self.em.load_bn()
        self.result_path = path_output
        self.wsUtils = WorldProgramUtils(self.am_rules, self.em_var)
        self.results = {}
        status = {
                    "yes": 0,
                    "no": 0,
                    "undecided": 0,
                    "unknown": 0,
                    "pyes": 0.0,
                    "pno": 0.0,
                    "pundecided": 0.0,
                    "punknown": 0.0
                }
        self.results["status"] = {lit : copy.copy(status) for lit in self.literals_to_consult}
    

    def start_exact_sampling(self):
        # Number of worlds
        n_worlds = pow(2, self.em_var) 
        known_programs = 0 
        print_ok("\nStarting exact sampling on " + str(n_worlds) + " world") 
        initial_time = time.time()
        for i in range(n_worlds): 
            print(i, end="\r")
            # Get world in list format
            world, evidence = self.wsUtils.id_world_to_format(i)
            # Get the probability of the world
            prob_world = self.em.get_sampling_prob(evidence)
            # Build the delp program for world
            delp_program, id_program = self.wsUtils.map_world_to_delp(self.model, world)
            status = ''
            if not self.wsUtils.known_program(id_program):
                # New delp
                status = query_to_delp(delp_program, self.literals_to_consult)
                self.wsUtils.save_program_status(id_program, status)
            else:
                # Known program
                status = self.wsUtils.get_status(id_program)
                known_programs += 1 
            for lit, status in status.items():
                self.results["status"][lit][status] += 1
                self.results["status"][lit]['p' + status] += prob_world
        
        execution_time = time.time() - initial_time
        self.results["data"] = {
                "n_worlds": n_worlds,
                "time": execution_time,
                "known_delp": known_programs
                }
        write_results(self.results, self.result_path)
