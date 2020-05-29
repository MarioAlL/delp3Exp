import numpy as np
import sys
from progress.bar import IncrementalBar
from utilsExp import *
from consultDeLP import *
from bnCode import *
import argparse

uniquePrograms = set()
bayesianNetwork, globalProgram, predicates, numberOfWorlds = '', '', '', 0
results = {
    'yes':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'no':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'und':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'unk':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'l':0.00,
    'u':1.00,
    'timeExecution':0,
    'worldsAnalyzed':0
}

def startSampling(literal, pathResult):
    global uniquePrograms
    dim = len(predicates) # Length to convert int to binary
    print_ok_ops('\nStarting exact sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    initialTime = time.time()
    for i in range(numberOfWorlds):
        worldData = int_to_bin_with_format(i, dim)
        world = worldData[0]
        evidence = worldData[1]
        prWorld = getSamplingProb(evidence)

        # Build the delp program for a world
        delpProgram = mapWorldToProgram(globalProgram, predicates, world)
        # Compute the literal status
        status = queryToProgram(delpProgram, literal, uniquePrograms)
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
        bar.next()
    bar.finish()
    results['worldsAnalyzed'] = numberOfWorlds
    timeExecution = time.time() - initialTime
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']
    results['timeExecution'] = timeExecution
    
    
    #Save file with results    
    with open(pathResult + 'exactResults.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)
   
    # Print the results
    print_ok_ops("Results: ")
    print("Unique programs: ", end='')
    print_ok_ops("%s" % (len(uniquePrograms)))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))

def main(literal, models, bn, pathResult):
    global globalProgram, predicates, bayesianNetwork, numberOfWorlds
    
    bayesianNetwork = bn
    globalProgram = models["af"]
    predicates = models["randomVar"]
    numberOfWorlds = pow(2,len(predicates))
    
    startSampling(literal, pathResult)
    

parser = argparse.ArgumentParser(description="Script to perform the Sampling experiment (Exact)")

parser.add_argument('-l',
                    help = 'The literal to calculate the probability interval',
                    action = 'store',
                    dest = 'literal',
                    required = True)
parser.add_argument('-p',
                    help='The DeLP3E program path',
                    action='store',
                    dest='program',
                    type=getDataFromFile,
                    required=True)
parser.add_argument('-bn',
                    help='The Bayesian Network file path (only "bifxml" for now)',
                    action='store',
                    dest='bn',
                    type=loadBN,
                    required=True)
parser.add_argument('-pathR',
                    help='Path to save the results (with file name)',
                    dest='pathResult',
                    required=True)

arguments = parser.parse_args()

main(arguments.literal, arguments.program, arguments.bn, arguments.pathResult)