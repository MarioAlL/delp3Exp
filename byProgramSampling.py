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

    
    def start_random_sampling(self, samples):
        lit_to_query = self.results["status"].keys()
        sampled_programs = np.random.choice(self.n_programs, samples, replace=True)
        unique_programs = list(set(sampled_programs))
        for sample_program in unique_programs:
            # Get program in list of 1 or 0 format
            in_list_format = self.wsUtils.id_program_to_format(sample_program)
            print(in_list_format)
            annot_status = [[rule[1], True] if in_list_format[index] == 1 else 
                                [rule[1], False] for index, rule in enumerate(self.model)]
            print(annot_status)
            print('\n')


