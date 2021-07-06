import copy
from utils import *
from consultDeLP import *
import time
import numpy as np


class Worlds:
    def __init__(self, model_path: str, save_path: str):
        # Utils to handle model
        self.utils = Model(model_path, save_path)
        # To save all results
        self.results = {}
        # To control repeated delp programs
        self.known_delp = KnownSamples()

    def consult_worlds(self, worlds: list, lit_to_query: list) -> float:
        """To iterate over sampled worlds consulting for literals"""
        initial_time = time.time()
        for sampled_world in worlds:
            # Get world in list format
            world, evidence = self.utils.id_world_to_bin(sampled_world)
            # Get the probability of the world
            prob_world = self.utils.em.get_sampling_prob(evidence)
            # Build the delp program for world
            delp_program, id_program = self.utils.map_world_to_delp(world)
            status = self.known_delp.search_sample(id_program)
            if status == -1:
                # New delp
                status = query_to_delp(delp_program, lit_to_query)
                self.known_delp.save_sample(id_program, status)
            for literal, response in status.items():
                # Update number of worlds
                self.results['status'][literal][response['status']] += 1
                # Update probabilities
                self.results['status'][literal]['p' + status['status']] += prob_world
                # Save time to compute the query in the world
                self.results['status'][literal]['time'] += status['time']
        print(self.utils.model_path + "<<Complete>>")
        execution_time = time.time() - initial_time
        return execution_time

    def start_sampling(self, percentile_samples: int, source: str, info: str) -> None:
        """Select randomly a subset of all possible worlds to perform an
        approximation of the exact interval"""
        # Total number of possible worlds
        n_worlds = self.utils.get_n_worlds()
        lit_to_query = self.utils.get_lit_to_consult()
        self.results['status'] = {lit: copy.copy(STATUS) for lit in lit_to_query}
        if percentile_samples == 100:
            # To compute the exact interval
            n_samples = n_worlds
            unique_worlds = range(n_samples)
            repeated_worlds = 0
        else:
            n_samples = get_int_percentile(percentile_samples, n_worlds)
            if source == 'distribution':
                # Sample from Probability Distribution Function
                unique_worlds, repeated_worlds = self.utils.em.gen_samples(n_samples)
            else:
                # Sample worlds randomly
                sampled_worlds = np.random.choice(n_worlds, n_samples, replace=True)
                unique_worlds = list(set(sampled_worlds))
                repeated_worlds = n_samples - len(unique_worlds)
        # Consult in each sampled world
        execution_time = self.consult_worlds(unique_worlds, lit_to_query)
        self.results['data'] = {
            'n_samples': n_samples,
            'time': execution_time,
            'repeated_worlds': repeated_worlds,
            'repeated_delp': n_samples - self.known_delp.get_unique_samples(),
            'unique_delp': self.known_delp.get_unique_samples()
        }
        write_results(self.results, self.utils.save_path, info)
