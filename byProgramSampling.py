import copy
from utils import *
from progress.counter import Counter
from consultDeLP import *
import time
import numpy as np
from sympy import *
import re


def def_vars_solver(annots: dict) -> None:
    """To define vars used in the model as symbols to use in the solver"""
    aux = [re.findall(r'\d+', annot) for key, annot in annots.items()]
    used_vars = [item for sublist in aux for item in sublist]
    in_list = list(set(used_vars))
    var(['x' + em_var for em_var in in_list])


def adapt_annots(annots: dict) -> dict:
    """To adapt annotations into valid expressions to use in the solver"""
    adapted_annots = {}
    for index, annot in enumerate(annots):
        if annots[annot].isdigit():
            adapted_annots[index] = {
                'True': '(x' + annots[annot] + ')',
                'False': '~(x' + annots[annot] + ')'
            }
        else:
            op_repl = annots[annot].replace("and", "&").replace("or", "|").replace("not", "~")
            in_list = op_repl.split(' ')
            expr = ' '.join(['x' + element if element.isdigit() else element for element in in_list])
            adapted_annots[index] = {
                'True': '(' + expr + ')',
                'False': '~(' + expr + ')'
            }
    return adapted_annots


def to_evidence(model: json) -> json:
    """To transform a model (values that satisfied a formula) in the format of evidences"""
    evidence = {}
    for k, v in model.items():
        if v:
            evidence[str(k)[1:]] = 1
        else:
            evidence[str(k)[1:]] = 0
    return evidence


class Programs:
    def __init__(self, model_path: str, save_path: str):
        # Utils to handle model
        self.utils = Model(model_path, save_path)
        # Define all variables in the programs to use in the solver
        def_vars_solver(self.utils.annotations)
        # Adapt annotations to use in the solver
        self.adapted_annots = adapt_annots(self.utils.annotations)
        # To save all results
        self.results = {}
        # To control repeated evidences
        self.known_evidences = []

    def start_sampling(self, percentile_samples: int, info: str) -> None:
        """To run exact compute of the interval or select randomly a subset of all
        possible programs (combining the values of its annotations) to perform an
        approximation of the exact interval"""
        n_programs = self.utils.get_n_programs()
        if percentile_samples == 100:
            # To compute the exact interval
            lit_to_query = self.utils.search_lit_to_consult()
            n_samples = n_programs
            unique_programs = range(n_programs)
            repeated_programs = 0   # ????
        else:
            lit_to_query = self.utils.get_interest_lit()
            n_samples = int(get_percentile(percentile_samples, n_programs))
            sampled_programs = np.random.choice(n_programs, n_samples, replace=True)
            unique_programs = list(set(sampled_programs))
            repeated_programs = n_samples - len(unique_programs)
        prog_data = self.consult_programs(unique_programs, self.adapted_annots, lit_to_query)
        execution_time, inconsistent_programs = prog_data
        self.results['data'] = {
            'n_samples': n_samples,
            'time': execution_time,
            'repeated_programs': repeated_programs,
            'inconsistent_programs': inconsistent_programs
        }
        write_results(self.results, self.utils.save_path, info)

    def consult_programs(self, unique_programs: list, adapted_annots: dict, lit_to_query: list) -> list:
        """To iterate over sampled programs consulting for literals"""
        rep_evid = 0 # To control...
        self.results['status'] = {lit: copy.copy(STATUS) for lit in lit_to_query}
        # To count the number of inconsistent programs sampled
        inconsistent_programs = 0
        counter = Counter('Processing programs: ', max=len(unique_programs))
        initial_time = time.time()
        for sampled_prog in unique_programs:
            sampled_in_bin = self.utils.id_prog_to_bin(sampled_prog)
            # Build the program from the sampled annotations
            self.replace_in_program(sampled_in_bin)
            # To create the expression that generate a sampled program
            expression = ''
            for index, value in enumerate(sampled_in_bin):
                if value == 1:
                    expression += adapted_annots[index]['True'] + ' & '
                else:
                    expression += adapted_annots[index]['False'] + ' & '
            flag = False
            program = self.utils.map_bin_to_prog(self.utils.prog_in_bin)
            status = query_to_delp(program, lit_to_query)
            prob = float(0.0)
            models = satisfiable(eval(expression[:-3]), all_models=True)
            for model in models:
                if model:
                    # The sampled program is consistent, is a valid program
                    evidence = to_evidence(model)
                    if evidence not in self.known_evidences:
                        # Get probability of the new evidence
                        prob += self.utils.em.get_sampling_prob(evidence)
                        self.known_evidences.append(evidence)
                    else:
                        rep_evid += 1
                else:
                    # To sampled program is inconsistent
                    inconsistent_programs += 1
                    flag = True
            if not flag:
                self.update_results(status, prob)
            counter.next()
        counter.finish()
        print(self.utils.model_path + " <<Complete>>")
        execution_time = time.time() - initial_time
        print("REPEATED EVIDENCES: ", rep_evid)
        return [execution_time, inconsistent_programs]

    def replace_in_program(self, sample: list) -> None:
        """To replace annotations status in the program"""
        for index, annot in enumerate(self.utils.annotations):
            self.utils.prog_in_bin[annot] = int(sample[index])

    def update_results(self, status: dict, prob: float) -> None:
        """To update results"""
        for literal, response in status.items():
            # Update number of worlds
            self.results['status'][literal][response['status']] += 1
            # Update probabilities
            self.results['status'][literal]['p' + response['status']] += prob
            # Save time to compute the query in the world
            self.results['status'][literal]['time'] += response['time']