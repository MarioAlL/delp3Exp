import numpy as np
import sys
from progress.bar import IncrementalBar
from utilsExp import *
from database import*
from datasets import *
from consultDeLP import *
import argparse

uniquePrograms = set()
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
    'timeExecution':0,
    'worldsAnalyzed':0
}

def startSampling(literal, pathResult):
    global uniquePrograms
    
    print_ok_ops('\nStarting exact sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    initialTime = time.time()
    for i in range(numberOfWorlds):
        world = allWorlds[i]
        # Build the delp program for a world
        delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
        # Compute the literal status
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

def main(literal, database, pathResult):
    global allWorlds, globalProgram, predicates, numberOfWorlds
    
    # NO DB NOW
    connectDB(database)
    allWorlds = getAllWorlds()
    globalProgram = getAf()
    predicates = getEM()
    numberOfWorlds = len(allWorlds)
    closeDB()
    
    startSampling(literal, pathResult)
    

parser = argparse.ArgumentParser(description="Script to perform the Sampling experiment (Exact)")

parser.add_argument('-l',
                    help = 'The literal to calculate the probability interval',
                    action = 'store',
                    dest = 'literal',
                    required = True)
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

arguments = parser.parse_args()

main(arguments.literal, arguments.dbName, arguments.pathResult)