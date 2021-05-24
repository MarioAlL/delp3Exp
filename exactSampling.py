import sys
import copy
from consultDeLP import *
from bn import *
from utilsExp import *
import time
import numpy as np

status = {
        "yes": 0,
        "no": 0,
        "undecided": 0,
        "unknown": 0,
        "pyes": 0.0,
        "pno": 0.0,
        "pundecided": 0.0,
        "punknown": 0.0,
        "time": 0.0
        }

class Sampling:
    def __init__(self, model_path: str, em_path: str, em_name: str, 
                                                            path_output: str):
        model = read_json_file(model_path)
        self.model = model["af"]
        self.em_var = model["em_var"]
        self.am_rules = len(model["af"])
        self.literals = model["literals"]
        self.em = BayesNetwork(em_name, em_path)
        self.em.load_bn()
        self.result_path = path_output + os.path.basename(model_path[:-5])
        self.wsUtils = WorldProgramUtils(self.am_rules, self.em_var)
        self.results = {} 

    
    def filter_literals(self) -> list:
        literals = []
        levels = list(self.literals.keys()) 
        # Simple one
        literals.append(np.random.choice(self.literals["0"], 1)[0])
        # Medium one
        from_levels = np.random.choice(levels[1:-1], 1)[0]
        literals.append(np.random.choice(self.literals[str(from_levels)],1)[0])
        #Complex one
        literals.append(np.random.choice(self.literals[levels[-1]],1)[0])

        self.results["status"] = {lit : copy.copy(status) for lit in literals}
        #return list(set(literals))
        return literals
    

    def start_exact_sampling(self):
        # Number of worlds
        n_worlds = pow(2, self.em_var) 
        known_programs = 0
        # Get the most "interesting" literals (from level > 0)
        lit_to_query = self.filter_literals()
        #print_ok("\nStarting exact sampling on " + str(n_worlds) + " worlds") 
        initial_time = time.time()
        for i in range(n_worlds):
            if i % 1000 == 0:
                print(i, end="\r")
            # Get world in list format
            world, evidence = self.wsUtils.id_world_to_format(i)
            # Get the probability of the world
            prob_world = self.em.get_sampling_prob(evidence)
            # Build the delp program for world
            delp_program, id_program = self.wsUtils.map_world_to_delp(self.model, world)
            status = self.wsUtils.known_program(id_program)
            if status == -1:
                # New delp
                status = query_to_delp(delp_program, lit_to_query)
                self.wsUtils.save_program_status(id_program, status)
            else:
                # Known program
                # status = self.wsUtils.get_status(id_program)
                known_programs += 1 
            for lit, status in status.items():
                self.results["status"][lit][status["status"]] += 1
                self.results["status"][lit]['p' + status["status"]] += prob_world
                self.results["status"][lit]["time"] += status["time"]
        print_ok(self.result_path + "complete")
        execution_time = time.time() - initial_time
        self.results["data"] = {
                "n_worlds": n_worlds,
                "time": execution_time,
                "known_delp": known_programs,
                "unique_programs": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)
