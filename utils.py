import re
import json
import os
from bn import BayesNetwork

"""Generals Names and Values"""
BN_NAMES = "BNdelp"
WIDTH_OF_INTEREST = 0.5
STATUS = {
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
"""General Utils"""


def read_json_file(path_file: str) -> json:
    """To read a json file"""
    try:
        file = open(path_file, "r")
        to_dict = json.load(file)
        file.close()
        return to_dict
    except IOError:
        print("Error trying to open the file %s" % path_file)
        exit()
    except ValueError:
        print("JSON incorrect format: %s" % path_file)
        exit()


def gfn(path: str) -> str:
    """Get the file name of a model specified in path"""
    return os.path.basename(path)


def gdn(path: str) -> str:
    """Get the directory name in a specified path"""
    return os.path.dirname(path)


def gfnexact(path: str) -> str:
    """Get the file name that contains the exact values of the model specified in path"""
    dir_name = os.path.dirname(path)
    model_name = gfn(path)[:-5]
    return dir_name + '/par/' + model_name + '_ep.json'


def to_decimal_format(number: float, decimals: int) -> str:
    """To format a float number"""
    return str(format(number, '.' + str(decimals) + 'f')).replace('.', ',')


def bin_to_int(in_binary: str) -> int:
    return int(in_binary, 2)


def gbn(index: str) -> str:
    """To return the Bayesian Network name of a model"""
    return BN_NAMES + index


def get_int_percentile(percentile: int, total: int) -> int:
    """Return the <percentile> percentile of <total> (the integer part)"""
    return int((percentile * 100) / total)


def write_results(results: json, path: str, approach: str) -> None:
    """To compute and save results"""
    n_samples = results['data']['n_samples']
    for lit, status in results['status'].items():
        status['percY'] = get_int_percentile(status['yes'], n_samples)
        status['percN'] = get_int_percentile(status['no'], n_samples)
        status['percU'] = get_int_percentile(status['undecided'], n_samples)
        status['percUNK'] = get_int_percentile(status['unknown'], n_samples)
        status['l'] = status['pyes']
        status['u'] = 1 - status['pno']
        if status['u'] - status['l'] <= WIDTH_OF_INTEREST:
            status['flag'] = "INTEREST"
    with open(path + approach + '.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)


def compute_metric(approximate: list, exact: list):
    """Compute the metric"""
    # approximate = [l,u]
    # exact = [l,u]
    width_approximate = approximate[1] - approximate[0]
    width_exact = exact[1] - exact[0]
    remainder_approximate = 1 - width_approximate
    remainder_exact = 1 - width_exact
    if remainder_exact == 0:
        metric = 0
    else:
        metric = remainder_approximate / remainder_exact
    return "{:.4f}".format(metric)


def format_annot(annot: str, world: list) -> str:
    """To transform annot into an expression from the values of a world"""
    to_eval = ''
    aux = annot.strip().split(' ')
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


def eval_annot(annot: str, world: list) -> bool:
    """To evaluate an annotation"""
    if annot == "" or annot == "True":
        return True
    elif annot == "not True":
        return False
    else:
        formatted_annot = format_annot(annot, world)
        return eval(formatted_annot)


def is_trivial_annot(annot: str) -> bool:
    """To evaluate if an annotation is 'trivial'"""
    if annot == 'True' or annot == '' or annot == 'not True':
        return True
    else:
        return False


class Model:
    """Class for model handling"""

    def __init__(self, model_path: str, save_path: str):
        self.model_path = model_path
        model_data = read_json_file(model_path)
        # The rule and annotations
        self.model = model_data['af']
        # The number of EM variables in the model
        self.em_vars = model_data['em_var']
        # The number of rules in the model
        self.am_rules_dim = len(self.model)
        # All literals used in the AM model
        self.literals_in_model = model_data['literals']
        # To load the Bayesian Network of the model
        index_model = re.search(r'\d+', gfn(model_path)).group()
        self.em = BayesNetwork(gbn(index_model), gdn(model_path))
        self.em.load_bn()
        self.save_path = save_path + gfn(model_path)[:-5]
        self.to_bin_delp_format = '{0:0' + str(self.am_rules_dim) + 'b}'
        self.to_bin_world_format = '{0:0' + str(self.em_vars) + 'b}'

    def get_n_worlds(self) -> int:
        """Return the total number of possible worlds"""
        return pow(2, self.em_vars)

    def id_delp_to_bin(self, id_delp: int) -> list:
        """To convert the id of a delp into a binary array"""
        delp = [int(digit) for digit in list(self.to_bin_delp_format.format(id_delp))]
        return delp

    def id_world_to_bin(self, id_world: int) -> list:
        """To convert the id of a world into a binary array and it's evidence"""
        world = [int(digit) for digit in list(self.to_bin_world_format.format(id_world))]
        evidence = {i: world[i] for i in range(len(world))}
        return [world, evidence]

    def map_bin_to_delp(self, bin_array: list) -> str:
        """Map a binary array into a delp"""
        delp = ''
        for index, value in enumerate(bin_array):
            if value == 1:
                # Add the rule
                delp += self.model[index][0]
        return delp

    def map_world_to_delp(self, world: list) -> list:
        """Map a world (in binary representation) into a delp"""
        delp = ''
        delp_in_bin = '0b'
        for rule, annot in self.model:
            check_annot = eval_annot(annot, world)
            if check_annot:
                delp += rule
                delp_in_bin += '1'
            else:
                delp_in_bin += '0'
        id_delp = bin_to_int(delp_in_bin)
        return [delp, id_delp]

    def get_lit_to_consult(self) -> list:
        """Return the literals with interest intervals of the model
        (for sampling)"""
        exact_file_name = gfnexact(self.model_path)
        literals = read_json_file(exact_file_name)['status'].keys()
        return literals


class KnownSamples:
    def __init__(self):
        self.samples = {}

    def search_sample(self, id_sample: int):
        try:
            return self.samples[id_sample]
        except KeyError:
            return -1

    def save_sample(self, id_sample: int, data: json) -> None:
        self.samples[id_sample] = data

    def get_unique_samples(self) -> int:
        return len(self.samples)
