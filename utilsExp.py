from termcolor import cprint
import json
import os
import glob
import copy
import re
import numpy as np
from sympy.logic.inference import satisfiable
from sympy import var

""" General Utils"""


def print_info(x): return cprint(x, 'grey', 'on_white')


def print_error(x): return cprint(x, 'red')


def print_ok(x): return cprint(x, 'green')


def gf4(number):
    return format(number, '.4f')


def gfn(model_path):
    "Get File Name"
    return os.path.basename(model_path)


def gfnexact(model_path):
    "Get File Name with exact values"
    dir_name = os.path.dirname(model_path)
    file_name = gfn(model_path)[:-5]
    return dir_name + '/par/' + file_name + 'output.json'


def gfnexactSam(result_path):
    dir_name = os.path.dirname(os.path.dirname(os.path.dirname(result_path)))
    return dir_name + '/par/'


def gbn(index):
    return 'BNdelp' + index


def is_always(annot):
    if annot == 'True' or annot == "":
        return 1
    elif annot == 'not True':
        return 0
    else:
        return 'x'


def compute_metric(aprox: list, exact: list):
    # aprox = [l,u]
    # exact = [l,u]
    width_aprox = aprox[1] - aprox[0]
    width_exact = exact[1] - exact[0]
    remainder_aprox = 1 - width_aprox
    remainder_exact = 1 - width_exact
    if remainder_exact == 0:
        metric = 0
    else:
        metric = remainder_aprox / remainder_exact
    return "{:.4f}".format(metric)


def read_json_file(path_file):
    try:
        file = open(path_file, "r")
        to_dict = json.load(file)
        file.close()
        return to_dict
    except IOError:
        # print(e)
        print_error("Error trying to open the file: %s" % path_file)
        exit()
    except ValueError:
        # print(e)
        print_error("JSON incorrect format: %s" % path_file)
        exit()


def get_all_delp(dataset_path):
    if not os.path.isdir(dataset_path):
        print_error("The specified path does not exist")
        exit()
    else:
        delp_programs = glob.glob(dataset_path + 'delp*.json')
        if len(delp_programs) != 0:
            return delp_programs
        else:
            print_error("The specified path is empty")
            exit()


def get_perc(number, total):
    return "{:.2f}".format((number * 100) / total)


def write_results(results: json, path: str):
    n_samples = results["data"]["n_samples"]
    for lit, status in results["status"].items():
        status["percY"] = get_perc(status["yes"], n_samples)
        status["percN"] = get_perc(status["no"], n_samples)
        status["percU"] = get_perc(status["undecided"], n_samples)
        status["percUNK"] = get_perc(status["unknown"], n_samples)
        status["l"] = status["pyes"]
        status["u"] = 1 - status["pno"]
        if status["u"] - status["l"] <= 0.5:
            status["flag"] = "INTEREST"

    with open(path + "output.json", 'w') as outfile:
        json.dump(results, outfile, indent=4)


""""""


class WorldProgramUtils:
    def __init__(self, am_dim: int, em_dim: int):
        self.am_dim = am_dim
        self.em_dim = em_dim
        self.to_format_program = '{0:0' + str(self.am_dim) + 'b}'
        self.to_format_world = '{0:0' + str(self.em_dim) + 'b}'
        # Dictionary to save the delp programs and literals status
        self.delp_programs = {}
        pass

    def known_program(self, id_program: int):
        try:
            return self.delp_programs[id_program]
        except KeyError:
            return -1

    def unique_programs(self) -> int:
        return len(self.delp_programs.keys())

    def map_bin_to_delp(self, model: list, delp_in_bin: list):
        delp = ''
        for index, value in enumerate(delp_in_bin):
            if value == 1:
                delp += model[index][0]
        return delp

    def map_world_to_delp(self, model: list, world: list):
        delp = ''
        delp_bin = '0b'
        for rule, form in model:
            check_form = self.check_form(form, world)
            if check_form:
                delp = delp + rule
                delp_bin += '1'
            else:
                delp_bin += '0'
        id_program = int(delp_bin, 2)
        return [delp, id_program]

    def save_program_status(self, id_program: int, status: json):
        self.delp_programs[id_program] = status

    def id_program_to_format(self, id_program):
        program = [int(digit) for digit in list(self.to_format_program.format(id_program))]
        return program

    def id_world_to_format(self, id_world):
        world = [int(digit) for digit in list(self.to_format_world.format(id_world))]
        evidence = {i: world[i] for i in range(len(world))}
        return [world, evidence]

    def format_form(self, form, world):
        to_eval = ''
        var_status = ''
        aux = form.strip().split(' ')
        for element in aux:
            try:
                if world[int(element)] == 1:
                    var_status = "True"
                else:
                    var_status = "False"
            except ValueError:
                var_status = element

            to_eval = to_eval + " " + var_status

        return to_eval

    def check_form(self, form: str, world: list):
        if form == "" or form == "True":
            return True
        else:
            return eval(self.format_form(form, world))

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
