import sys

from progress.bar import IncrementalBar
from consultDeLP import *
from em.bn import *
import time
import argparse

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
    print_ok_ops('\nStarting exact sampling...')
    initialTime = time.time()
    for i in range(numberOfWorlds):
        #if i % 1000 == 0:
        print (i, end="\r")
        worldData = int_to_bin_with_format(i, dim)
        world = worldData[0]
        evidence = worldData[1]
        prWorld = bayesian_network.get_sampling_prob(evidence)

        # Build the delp program for a world
        delpProgram = map_world_to_program(globalProgram, predicates, world)
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
    predicates = models["randomVar"]
    numberOfWorlds = pow(2, len(predicates))
    startSampling(literal, bayesian_network, path_to_save, solverName)


# parser = argparse.ArgumentParser(description="Script to perform the Sampling experiment (Exact)")
#
# parser.add_argument('-l',
#                     help='The literal to calculate the probability interval',
#                     action='store',
#                     dest='literal',
#                     required=True)
#
# arguments = parser.parse_args()

# pathToProgram = "/home/mario/results/final/models.json"
# pathResult = "/home/mario/results/final/"
# program = getDataFromFile(pathToProgram)
# myBN = BayesNetwork('TEST', '/home/mario/results/final/')
# myBN.load_bn()

solverName = sys.argv[5]
literalToConsult = sys.argv[4]
pathToProgram = sys.argv[0]
pathResult = sys.argv[1]
program = getDataFromFile(pathToProgram)
myBN = BayesNetwork(sys.argv[2] + 'TEST', sys.argv[3])
myBN.load_bn()
main(literalToConsult, program, myBN, pathResult, solverName)