import json
import os
"""Generals Names and Values"""
BN_NAMES = "BNdelp"
WIDTH_OF_INTEREST = 0.5

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


def gfnexact(path: str) -> str:
    """Get the file name with the exact values of the model specified in path"""
    dir_name = os.path.dirname(path)
    model_name = gfn(path)[:-5]
    return dir_name + '/par/' + model_name + '_ep.json'


def to_format(number: float, decimals: int) -> str:
    """To format a float number"""
    return str(format(number, '.' + str(decimals) + 'f')).replace('.', ',')


def gbn(index: str) -> str:
    """To return the Bayesian Network name of a model"""
    return BN_NAMES + index


def get_percentile(perc: int, total: int) -> int:
    """Return the <perc> percentile of <total> (the integer part)"""
    return int((perc * 100) / total)


def write_results(results: json, path:str, approach: str) -> None:
    """To compute and save results"""
    n_samples = results['data']['n_samples']
    for lit, status in results['status'].items():
        status['percY'] = get_percentile(status['yes'], n_samples)
        status['percN'] = get_percentile(status['no'], n_samples)
        status['percU'] = get_percentile(status['undecided'], n_samples)
        status['percUNK'] = get_percentile(status['unknown'], n_samples)
        status['l'] = status['pyes']
        status['u'] = 1 - status['pno']
        if status['u'] - status['l'] <= WIDTH_OF_INTEREST:
            status['flag'] = "INTEREST"
    with open(path + approach + '.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)


def compute_metric(approximate: list, exact: list):
    """Compute the metric"""
    # aproximate = [l,u]
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


"""End General Utils"""