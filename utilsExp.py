import json
import os
import glob
import copy
import re
import numpy as np
from sympy.logic.inference import satisfiable
from sympy import var


class WorldProgramUtils:
    def __init__(self, am_dim: int, em_dim: int):
        self.am_dim = am_dim
        self.em_dim = em_dim
        self.to_format_program = '{0:0' + str(self.am_dim) + 'b}'
        self.to_format_world = '{0:0' + str(self.em_dim) + 'b}'
        # Dictionary to save the delp programs and literals status
        self.delp_programs = {}
        pass

    def is_evidence_ok(self, evidence, key, value):
        try:
            if evidence[key] == value:
                return True
            else:
                return False
        except KeyError:
            return True

    def get_program_evidence(self, rule_annot_status):
        delp_program = ''
        evidence = {}
        for rule, annot, status in rule_annot_status:
            if annot == "True" or annot == "":
                delp_program += rule
            elif annot == "not True":
                pass
            else:
                em_var = re.search(r'\d+', annot).group()
                if status:
                    # The annotation must be True
                    if 'not' in annot:
                        # The em_var must be False
                        if self.is_evidence_ok(evidence, em_var, 0):
                            evidence[em_var] = 0
                            delp_program += rule
                        else:
                            # Inconsisten Program
                            return [-1, -1]
                            break
                    else:
                        # The em_var must be True
                        if self.is_evidence_ok(evidence, em_var, 1):
                            evidence[em_var] = 1
                            delp_program += rule
                        else:
                            # Inconsisten Program
                            return [-1, -1]
                            break
                else:
                    # The annotation must be False
                    if 'not' in annot:
                        # The em_var must be True
                        if self.is_evidence_ok(evidence, em_var, 1):
                            evidence[em_var] = 1
                        else:
                            # Inconsisten Program
                            return [-1, -1]
                            break
                    else:
                        # The em_var must be False 
                        if self.is_evidence_ok(evidence, em_var, 0):
                            evidence[em_var] = 0
                        else:
                            # Inconsisten Program
                            return [-1, -1]
                            break
        return [delp_program, evidence]

    def get_sub_worlds(self, rule_annot_status, perc_samples, exact):
        # Compute and return worlds that generate differents delp programs
        # this worlds only consider the em variables that are used in the 
        # program's annotation
        sub_worlds = []
        aux = [re.findall(r'\d+', annot[1]) for annot in rule_annot_status]
        used_vars = [item for sublist in aux for item in sublist]
        in_list = list(set(used_vars))
        n_used_vars = len(in_list)

        sub_world_format_binary = '{0:0' + str(n_used_vars) + 'b}'
        n_unique_delp = pow(2, n_used_vars)
        if not exact:
            samples = int((perc_samples * n_unique_delp) / 100)
            random_sub_worlds = np.random.choice(n_unique_delp, samples, replace=True)
            unique_sub_worlds = list(set(random_sub_worlds))
            for sub_world in unique_sub_worlds:
                sub_world_format = ['s'] * self.em_dim
                sub_world_values = sub_world_format_binary.format(sub_world)
                evidence = {}
                for index, var in enumerate(in_list):
                    sub_world_format[int(var)] = int(sub_world_values[index])
                    evidence[var] = int(sub_world_values[index])
                sub_worlds.append([sub_world_format, evidence])
            repetead_sub_world = samples - len(unique_sub_worlds)
            return [sub_worlds, repetead_sub_world, samples]
        else:
            for s_world in range(n_unique_delp):
                sub_world_format = ['s'] * self.em_dim
                sub_world_values = sub_world_format_binary.format(s_world)
                evidence = {}
                for index, var in enumerate(in_list):
                    sub_world_format[int(var)] = int(sub_world_values[index])
                    evidence[var] = int(sub_world_values[index])
                sub_worlds.append([sub_world_format, evidence])
            return [sub_worlds, 0, n_unique_delp]

    def adapt_annot(self, annot):
        if annot.isdigit():
            return 'x' + annot
        else:
            op_repl = annot.replace("and", "&").replace("or", "|").replace("not", "~")
            in_list = op_repl.split(' ')
            expr = ' '.join(['x' + element if element.isdigit() else element for element in in_list])
            return expr

    def to_evidence(self, model):
        evidence = {}
        for k, v in model.items():
            if v:
                evidence[str(k)[1:]] = 1
            else:
                evidence[str(k)[1:]] = 0
        return evidence

    def get_sampled_annot(self, annot, perc_samples, exact):
        samples_evid = {}
        # To construct and evaluate annotations
        aux = [re.findall(r'\d+', an[1]) for an in annot]
        used_vars = [item for sublist in aux for item in sublist]
        in_list = list(set(used_vars))
        var(['x' + em_var for em_var in in_list])
        #
        n_annot = len(annot)
        combinations = pow(2, n_annot)
        format_annot = '{0:0' + str(n_annot) + 'b}'
        if not exact:
            samples = int((perc_samples * combinations) / 100)
            # samples = 1
            sampled_values = np.random.choice(combinations, samples, replace=False)
            unique_samples = list(set(sampled_values))
        else:
            samples = combinations
            unique_samples = range(combinations)
        # for sample in range(combinations):
        for sample in unique_samples:
            true_list = []
            false_list = []
            sample_in_bin = format_annot.format(sample)
            samples_evid[sample_in_bin] = []
            for index, value in enumerate(sample_in_bin):
                if value == '1':
                    true_list.append(self.adapt_annot(annot[index][1]))
                else:
                    false_list.append('~(' + self.adapt_annot(annot[index][1]) + ')')
            if len(true_list) != 0 and len(false_list) != 0:
                expression = '(' + ' & '.join(true_list) + ') & (' + ' & '.join(false_list) + ')'
            elif len(true_list) != 0:
                expression = ' & '.join(true_list)
            else:
                expression = '( ' + ' & '.join(false_list) + ' )'
            models = satisfiable(eval(expression), all_models=True)
            for model in models:
                if model:
                    samples_evid[sample_in_bin].append(self.to_evidence(model))
        return {
            'samples_evid': {k: v for k, v in samples_evid.items() if v != []},
            'samples': samples,
            'repeated': samples - len(unique_samples)
        }
