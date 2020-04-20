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

# plt.style.use('fivethirtyeight')
def handlerTimer(signum, frame):
    #print("Time over")
    raise Exception("Time over")

def startSampling(literal, timeout, pathResult):
    yW, nW, undW, unkW, empty = 0, 0, 0, 0, 0
    probY, probN, probUnd, probUnk, probEmpty = 0.00, 0.00, 0.00, 0.00, 0.00
    
    #To graph
    world_data = 0
    elapsed_data = 0
    timeExecution = []

    globalProgram = getAf()
    predicates = getEM()
    numberOfWorlds = pow(2, len(predicates))
    print("Loading from db...")
    allWorlds = getAllWorlds()
    print("Worlds loaded")
    uniquesWorlds = set() #Ids
    uniquePrograms = set() # [[program],[status]]
    print('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    #worldsIds = np.random.choice(numberOfWorlds, samples, replace=False)
    initialTime = time.time()
    signal.signal(signal.SIGALRM, handlerTimer)
    print_ok_ops("\nTime setting: " + str(timeout) + " seconds")
    signal.alarm(timeout)
    try:
            for i in range(numberOfWorlds):
                worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
                #worldRandomId = worldsIds[i]
                if(not worldRandomId in uniquesWorlds):
                    uniquesWorlds.add(worldRandomId)
                    #world = getWorldById(0) # The binary array
                    world = allWorlds[worldRandomId]
                    # Build the PreDeLP Program for a world
                    delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
                    status = queryToProgram(delpProgram, literal, uniquePrograms)
                    if status[1] == 'yes':
                            yW += 1
                            probY = probY + world['prob']
                    elif status[1] == 'no':
                            nW += 1
                            probN = probN + world['prob']
                    elif status[1] == 'undecided':
                            undW += 1
                            probUnd = probUnd + world['prob']
                    elif status[1] == 'unknown':
                            unkW += 1
                            probUnk = probUnk + world['prob']

                world_data = i
                elapsed_data = time.time() - initialTime
                timeExecution.append([world_data, elapsed_data])

                bar.next()
            bar.finish()
            
            signal.alarm(0)
        
    except Exception as e:
        print('\n')
        print_error_msj(e)
        signal.alarm(0)
    
    #print_ok_ops("Results: ")
    #print("Unique worlds: %s" % (len(uniquesWorlds)))
    #print("Unique programs: %s" % (len(uniquePrograms)))
    #print("Yes worlds: \t\t %s \t\t\t Prob =  %.4f" % (yW, probY))
    #print("No worlds: \t\t %s \t\t\t Prob =  %.4f" % (nW, probN))
    #print("Undecided worlds: \t %s \t\t\t Prob =  %.4f" % (undW, probUnd))
    #print("Unknow worlds: \t\t %s \t\t\t Prob =  %.4f" % (unkW, probUnk))
    prob = [probY, 1.00 - probN]
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, prob[0], prob[1]))
    
    times = {
        "experiment": "Random",
        "timeExecution": [timeExecution[-1][1]],
        "prob": [literal, prob[0], prob[1]],
        'results' : {
                'yW': yW,
                'probY': probY,
                'nW': nW,
                'probN': probN,
                'undW': undW,
                'probUnd': probUnd,
                'unkW': unkW,
                'probUnk': probUnk,
            },
        'worldsAnalyzed': world_data
    }
    with open(pathResult + 'timeRandomResults.json', 'w') as outfile:
        json.dump(times, outfile)


def main(literal, timeout, database, pathResult):
    connectDB(database)
    startSampling(literal, timeout, pathResult)
    closeDB()

parser = argparse.ArgumentParser(description="Script to perform the Sampling experiment (Random)")

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
parser.add_argument('-t',
                    help='Seconds to execute',
                    dest='timeout',
                    type=int,
                    required=True)
arguments = parser.parse_args()

main(arguments.literal, arguments.timeout, arguments.dbName, arguments.pathResult)
