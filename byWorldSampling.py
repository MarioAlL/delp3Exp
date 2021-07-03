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

class WorldSampling:
    def __init__(self, model_path: str, em_path: str, em_name: str, 
                                                            path_output: str,
                                                            literals: dict):
        model = read_json_file(model_path)
        self.model = model["af"]
        self.em_var = model["em_var"]
        self.am_rules = len(model["af"])
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


    def start_random_sampling(self, perc_samples: int) -> None:
        known_programs = 0
        n_worlds = pow(2, self.em_var)
        samples = int((perc_samples * n_worlds) / 100)
        lit_to_query = self.results["status"].keys()
        sampled_worlds = np.random.choice(n_worlds, samples, replace=True)
        unique_worlds = list(set(sampled_worlds))
        initial_time = time.time()
        for sample_world in unique_worlds:
            # Get world in list format
            world, evidence = self.wsUtils.id_world_to_format(sample_world)
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
            self.update_lit_status(status, prob_world) 
        print_ok(self.result_path + " complete")
        execution_time = time.time() - initial_time
        self.results["data"] = {
                "n_samples": samples,
                "time": execution_time,
                "repeated_delp": known_programs,
                "repeated_worlds": len(sampled_worlds) - len(unique_worlds),
                "unique_programs": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)


    def start_distribution_sampling(self, perc_samples: int, ) -> None:
        known_programs = 0
        lit_to_query = self.results["status"].keys()
        # Sampling from probability distribution
        #   return unique worlds and the number of repetead worlds
        #   sampled_worlds[0] = list of unique worlds
        #   sampled_worlds[1] = int that represent the number of rep worlds
        n_worlds = pow(2, self.em_var)
        samples = int((perc_samples * n_worlds) / 100)
        sampled_worlds = self.em.gen_samples(samples)
        repeated_worlds = sampled_worlds[1]
        initial_time = time.time()
        for sample_world in sampled_worlds[0]:
            # Get world in list format
            world, evidence = sample_world
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
                known_programs += 1
            self.update_lit_status(status, prob_world)
        print_ok(self.result_path + " complete")
        execution_time = time.time() - initial_time
        self.results["data"] = {
                "n_samples": samples,
                "time": execution_time,
                "repeated_delp": known_programs,
                "repeated_worlds": repeated_worlds,
                "unique_programs": self.wsUtils.unique_programs()
                }
        write_results(self.results, self.result_path)



