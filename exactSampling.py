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

class Exact:
    def __init__(self, model_path, em_path, em_name, path_output):
        """
        :params
            -model_path: str
            -em_path: str
            -em_name: str
            -path_output: str
        """
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

    
    def update_lit_status(self, status, prob_world):
        for lit, status in status.items():
            self.results["status"][lit][status["status"]] += 1
            self.results["status"][lit]['p' + status["status"]] += prob_world
            self.results["status"][lit]["time"] += status["time"]
    

    def get_all_literals(self):
        literals = []
        for level, lits in self.literals.items():
            literals.append(lits)    
        lit_list = [item for sublist in literals for item in sublist]
        lit_l = list(set(lit_list))
        self.results["status"] = {lit : copy.copy(status) for lit in lit_l}
        return lit_l

    def filter_literals(self):
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
        return literals
    

    def start_world_exact_sampling(self):
        # Number of worlds
        n_worlds = pow(2, self.em_var) 
        known_programs = 0
        # Get the most "interesting" literals (from level > 0)
        lit_to_query = self.filter_literals()
        initial_time = time.time()
        for i in range(n_worlds):
            print(i, end="\r")
            # Get world in list format
            world, evidence = self.wsUtils.id_world_to_format(i)
            # Get the probability of the world
            prob_world = self.em.get_sampling_prob(evidence)
            # Build the delp program for world
            delp_info = self.wsUtils.map_world_to_delp(self.model, world)
            delp_program, id_program = delp_info
            status = self.wsUtils.known_program(id_program)
            if status == -1:
                # New delp
                status = query_to_delp(delp_program, lit_to_query)
                self.wsUtils.save_program_status(id_program, status)
            else:
                # Known program
                # status = self.wsUtils.get_status(id_program)
                known_programs += 1 
            self.update_lit_status(status, prob_world) 
        print_ok(self.result_path + " complete")
        execution_time = time.time() - initial_time
        self.results["data"] = {
                "n_samples": n_worlds,
                "time": execution_time,
                "known_delp": known_programs,
                "unique_programs": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)

    
    def start_program_exact_sampling(self):
        # Con errores, ya que no itero sobre todos los posibles programas.
        # Itero sobre todas las posibles combinaciones de mundos (subconjunto de 
        # todos los mundos posibles en los cuales se cambian solo las variables que 
        # son utilizadas en el programa), es decir, puede haber programas repetidos.
        known_programs = 0
        lit_to_query = self.filter_literals()
        #lit_to_query = self.get_all_literals()
        rule_annot = self.model
        initial_time = time.time()
        # Pre filter
        sub_worlds_info = self.wsUtils.get_sub_worlds(rule_annot, 100, True)
        sub_worlds_evidences, rep_subworlds, sampled_programs = sub_worlds_info
        print_ok(len(sub_worlds_evidences))
        for sub_world in sub_worlds_evidences:
            prob_world = self.em.get_sampling_prob(sub_world[1])
            # Build the delp program for world
            delp_info = self.wsUtils.map_world_to_delp(self.model, sub_world[0])
            delp_program, id_program = delp_info
            status = self.wsUtils.known_program(id_program)
            if status == -1:
                # New delp
                status = query_to_delp(delp_program, lit_to_query)
                self.wsUtils.save_program_status(id_program, status)
            else:
                # Known program
                known_programs += 1
            self.update_lit_status(status, prob_world)
        print_ok(self.result_path + " Complete")
        execution_time = time.time() - initial_time
        repetead_programs = rep_subworlds + known_programs
        self.results["data"] = {
                "n_samples": sampled_programs,
                "time": execution_time,
                "repetead_delp": repetead_programs,
                "unique_delp": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)
