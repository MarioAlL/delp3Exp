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

class ProgramSampling:
    def __init__(self, model_path, em_path, em_name, path_output, literals):
        model = read_json_file(model_path)
        self.model = model["af"] # List with all rules
        self.em_var = model["em_var"]
        self.am_rules = len(model["af"]) # Number of rules
        self.n_programs = pow(2, self.am_rules) # Number possible programs
        self.em = BayesNetwork(em_name, em_path)
        self.em.load_bn()
        self.result_path = path_output + os.path.basename(model_path[:-5])
        self.wsUtils = WorldProgramUtils(self.am_rules, self.em_var)
        self.results = {}
        self.results["status"] = {lit: copy.copy(status) for lit in literals}
    

    def update_lit_status(self, status, prob_world):
        for lit, status in status.items():
            self.results["status"][lit][status["status"]] += 1
            self.results["status"][lit]['p' + status["status"]] += prob_world
            self.results["status"][lit]["time"] += status["time"]

    
    def start_random_sampling(self, samples):
        inconsistent_programs = 0
        lit_to_query = self.results["status"].keys()
        sampled_programs = np.random.choice(self.n_programs, samples, 
                                                                replace=True)
        unique_programs = list(set(sampled_programs))
        initial_time = time.time()
        for sample_program in unique_programs:
            # Get program in list of 1 or 0 format
            in_list_format = self.wsUtils.id_program_to_format(sample_program)
            rule_annot_status = [[rule[0], rule[1], True] if 
                                            in_list_format[index] == 1 else 
                                [rule[0], rule[1], False] for index, rule in 
                                                        enumerate(self.model)]
            # Get the subprogram and its evidence
            prog_evid = self.wsUtils.get_program_evidence(rule_annot_status)
            # Controlar si es un programa correcto?
            delp_program, evidence = prog_evid
            if delp_program != -1:
                prob_world = self.em.get_sampling_prob(evidence)
                if prob_world != -1:
                    # Possible program
                    # Query to delp program (no existen programas repetidos)
                    status = query_to_delp(delp_program, lit_to_query)
                    self.update_lit_status(status, prob_world)
                else:
                    # Prob join = 0
                    inconsistent_programs += 1
            else:
                # Inconsisten Program
                inconsistent_programs += 1
        print_ok(self.result_path + " complete")
        execution_time = time.time() - initial_time
        repetead_programs = samples - len(unique_programs)
        self.results["data"] = {
                "n_samples": samples,
                "time": execution_time,
                "repetead_delp": repetead_programs,
                "inconsistent_delp": inconsistent_programs,
                "unique_delp": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)


    def start_prefilter_sampling(self, perc_samples):
        print(self.result_path)
        inconsistent_programs = 0
        lit_to_query = self.results["status"].keys()
        rule_annot_status = [[rule[0], rule[1], True] for rule in self.model]
        initial_time = time.time()
        sub_worlds_rep = self.wsUtils.get_sub_worlds_random(rule_annot_status, 
                                                                    perc_samples, 
                                                                    False)
        sub_worlds_evidences = sub_worlds_rep[0]
        for sub_world in sub_worlds_evidences:
            prob_world = self.em.get_sampling_prob(sub_world[1])
            # Build the delp program for world
            delp_program, id_program = self.wsUtils.map_world_to_delp(self.model, sub_world[0])
            status = self.wsUtils.known_program(id_program)
            if status == -1:
                # New delp
                status = query_to_delp(delp_program, lit_to_query)
                self.wsUtils.save_program_status(id_program, status)
            else:
                # Known program
                known_programs += 1
            self.update_lit_status(status, prob_world)
        print_ok(self.result_path + " complete")
        execution_time = time.time() - initial_time
        repetead_programs = sub_worlds_rep[1]
        self.results["data"] = {
                "n_samples": sub_worlds_rep[2],
                "time": execution_time,
                "repetead_delp": repetead_programs,
                "inconsistent_delp": inconsistent_programs,
                "unique_delp": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)
