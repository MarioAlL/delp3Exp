import sys
sys.path.insert(3, './DeLPSolver/')
sys.path.insert(1, './EM/BNs/')
sys.path.insert(2, './Utils/')
from progress.bar import IncrementalBar
from consultDeLP import *
from bn import *
from utilsExp import *
import time
import argparse
utils = Utils()
uniquePrograms = set()
globalProgram, predicates, numberOfWorlds = '', '', ''
results = {
    'yes': {
        'total': 0,
        'perc': 0.00,
        'prob': 0.00
    },
    'no': {
        'total': 0,
        'perc': 0.00,
        'prob': 0.00
    },
    'und': {
        'total': 0,
        'perc': 0.00,
        'prob': 0.00
    },
    'unk': {
        'total': 0,
        'perc': 0.00,
        'prob': 0.00
    },
    'l': 0.00,
    'u': 1.00,
    'timeExecution': 0,
    'worldsAnalyzed': 0
}


def startSampling(literal, bayesian_network, path_result, solverName):
    global uniquePrograms
    dim = len(predicates)  # Length to convert int to binary
    utils.print_ok('\nStarting exact sampling...')
    initialTime = time.time()
    for i in range(numberOfWorlds):
        #if i % 1000 == 0:
        print (i, end="\r")
        worldData = utils.int_to_bin_with_format(i, dim)
        world = worldData[0]
        evidence = worldData[1]
        prWorld = bayesian_network.get_sampling_prob(evidence) 
        # Build the delp program for a world
        delpProgram = utils.map_world_to_program(globalProgram, predicates, world)
        # Compute the literal status
        status = queryToProgram(delpProgram, literal, uniquePrograms, solverName)
        if status[1] == 'yes':
            results['yes']['total'] += 1
            results['yes']['prob'] = results['yes']['prob'] + prWorld
        elif status[1] == 'no':
            results['no']['total'] += 1
            results['no']['prob'] = results['no']['prob'] + prWorld
        elif status[1] == 'undecided':
            results['und']['total'] += 1
            results['und']['prob'] = results['und']['prob'] + prWorld
        elif status[1] == 'unknown':
            results['unk']['total'] += 1
            results['unk']['prob'] = results['unk']['prob'] + prWorld
    results['worldsAnalyzed'] = numberOfWorlds
    time_execution = time.time() - initialTime
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']
    results['timeExecution'] = time_execution

    flag = ''
    # if results['u'] - results['l'] < 0.3:
    #     flag = 'INTEREST'

    # Save file with results
    with open(path_result + flag +'exactResults.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)

    # Print the results
    # print_ok_ops("Results: ")
    # print("Unique programs: ", end='')
    # print_ok_ops("%s" % (len(uniquePrograms)))
    # print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))


def main(literal, models, bn, path_to_save, solverName):
    global globalProgram, predicates, numberOfWorlds

    bayesian_network = bn
    globalProgram = models["af"]
    predicates = list(range(models["em_var_use_ann"]))
    numberOfWorlds = pow(2, len(predicates))
    startSampling(literal, bayesian_network, path_to_save, solverName)

literal = 'a_0'
models = utils.getDataFromFile("../modelsdelp3e/ssm/modeldelp0.json")
em_model = BayesNetwork("BNdelp0", "../modelsdelp3e/ssm/")
em_model.load_bn()
path_to_save = "./"
solverName = "globalCore"

main(literal, models, em_model, path_to_save, solverName)
