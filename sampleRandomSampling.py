import numpy as np
import sys
import matplotlib.pyplot as plt
import signal
from progress.bar import IncrementalBar
from utilsExp import *
from database import*
from datasets import *
from consultDeLP import *
import argparse

uniquePrograms, uniquesWorlds = set(), set()
allWorlds, globalProgram, predicates, numberOfWorlds = '', '', '', 0
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
    'timeExecution':[],
    'worldsAnalyzed':0
}

def startSampling(literal, samples, pathResult):
    global uniquesWorlds, uniquePrograms

    print('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=samples)
    initialTime = time.time()
    for i in range(samples):
        worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
        if(not worldRandomId in uniquesWorlds):
            uniquesWorlds.add(worldRandomId)
            world = allWorlds[worldRandomId]
            # Build the PreDeLP Program for a world
            delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status[1] == 'yes':
                results['yes']['total'] += 1
                results['yes']['prob'] = results['yes']['prob'] + world['prob']
            elif status[1] == 'no':
                results['no']['total'] += 1
                results['no']['prob'] = results['no']['prob'] + world['prob']
            elif status[1] == 'undecided':
                results['und']['total'] += 1
                results['und']['prob'] = results['und']['prob'] + world['prob']
            elif status[1] == 'unknown':
                results['unk']['total'] += 1
                results['unk']['prob'] = results['unk']['prob'] + world['prob']
        bar.next()
    bar.finish()
    results['timeExecution'].append(time.time() - initialTime)
    results['worldsAnalyzed'] = samples
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']
    
    #Save file with results    
    with open(pathResult + 'sampleRandomResults.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)
   
    # Print the results
    print_ok_ops("Results: ")
    print("Unique worlds: %s" % (len(uniquesWorlds)))
    print("Unique programs: %s" % (len(uniquePrograms)))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))


def main(literal, samples, database, pathResult):
    global allWorlds, globalProgram, predicates, numberOfWorlds
    
    connectDB(database)
    allWorlds = getAllWorlds()
    globalProgram = getAf()
    predicates = getEM()
    numberOfWorlds = len(allWorlds)
    closeDB()

    startSampling(literal, samples, pathResult)


parser = argparse.ArgumentParser(
    description="Script to perform the Sampling experiment (Random)")

parser.add_argument('-l',
                    help='The literal to calculate the probability interval',
                    action='store',
                    dest='literal',
                    required=True)
parser.add_argument('-db',
                    help='The database name where load the data',
                    action='store',
                    dest='dbName',
                    type=controlDBExist,
                    required=True)
parser.add_argument('-pathR',
                    help='Path to save the results (with file name)',
                    dest='pathResult',
                    required=True)
parser.add_argument('-s',
                    help='Number of samples (in random setting)',
                    dest='samples',
                    type=int,
                    required=True)
arguments = parser.parse_args()

main(arguments.literal, arguments.samples, arguments.dbName, arguments.pathResult)
