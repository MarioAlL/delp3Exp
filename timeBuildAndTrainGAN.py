
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import numpy as np
import signal
from tensorflow.keras import layers
import time
from progress.bar import IncrementalBar
from datasets import *
from buildYesGAN import *
from buildNoGAN import *
tf.get_logger().setLevel('ERROR')
tf.get_logger().warning('test')

existYesModel, existNoModel = False, False
# uniqueWorlds = Worlds Programs {(1,0,...,0),(1,0,...,0)}
# uniqueWorldsIds = Ids {(id),(id)}
# uniquePrograms = {(program),(status)}
uniquesWorlds, uniquePrograms = set(), set()
world_data = 0
trainingAndGenTime = []
allWorlds, globalProgram, predicates, numberOfWorlds = '', '', '', 0
timeoutGuided = 0
results = {
    'yW':0,
    'nW':0,
    'undW':0,
    'unkW':0,
    'prY':0.00,
    'prN':0.00,
    'prUnd':0.00,
    'prUnk':0.00,
    'l':0.00,
    'u':1.00,
    'timeExecution':'',
    'worldsAnalyzed':0
}

def handlerTimer(signum, frame):
    #print("Time over")
    raise Exception("Time over")

def searchTrainDataset(literal, timeout):
    global world_data, results, uniquesWorlds, uniquePrograms
    datasetYes, datasetNo = [], []
   
    signal.signal(signal.SIGALRM, handlerTimer)
    print_ok_ops("\nTime setting (Sampling): " + str(timeout) + " seconds")
    print('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    initialTime = time.time()
    signal.alarm(timeout)
    try:
        for i in range(numberOfWorlds):
            worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
            world = allWorlds[worldRandomId]
            worldValues = tuple(world['program'])
            if(not worldValues in uniquesWorlds):
                uniquesWorlds.add(worldValues)
                # Build the PreDeLP Program for a world
                delpProgram = mapWorldToProgram(globalProgram, predicates, world['program']) #return [[string],[bin]]
                status = queryToProgram(delpProgram, literal, uniquePrograms) #return (program, status)
                if status[1] == 'yes':
                        results['yW'] += 1
                        results['prY'] = results['prY'] + world['prob']
                        datasetYes.append(world['program'])
                elif status[1] == 'no':
                        results['nW'] += 1
                        results['prN'] = results['prN'] + world['prob']
                        datasetNo.append(world['program'])
                elif status[1] == 'undecided':
                        results['undW'] += 1
                        results['prUnd'] = results['prUnd'] + world['prob']
                elif status[1] == 'unknown':
                        results['unkW'] += 1
                        results['prUnk'] = results['prUnk'] + world['prob']
            world_data += 1
            bar.next()
        
        bar.finish()

    except Exception as e:
        print('\n')
        print_error_msj(e)
        
    signal.alarm(0)
    print_ok_ops('Length of training data set found (Yes): %s' % (len(datasetYes)))
    print_ok_ops('Length of training data set found (No): %s' % (len(datasetNo)))
    # print("yes Worlds: " + str(results['yW']))
    # print("no Worlds: " + str(results['nW']))
    # print("Undecided Worlds: " + str(results['undW']))
    trainingAndGenTime.append(time.time() - initialTime) # Time to random sampling
    return [datasetYes, datasetNo]
    
def samplingAndTraining(literal, timeoutSampling, timeoutTraining, pathResult):
    global existNoModel, existYesModel, world_data, timeoutGuided

    # Search a training dataset
    # trainingDatasetes[0] = 'yes'
    # trainingDatasetes[1] = 'no'
    trainingDatasets = searchTrainDataset(literal, timeoutSampling)
    
    print_ok_ops("\nTime setting (Training): " + str(timeoutTraining) + " seconds")
    initialTime = time.time()
    
    if(len(trainingDatasets[0]) != 0 and len(trainingDatasets[1]) != 0):
        timeTrainingEachGan = int(timeoutTraining/2)
    elif (len(trainingDatasets[0]) == 0 and len(trainingDatasets[1]) == 0):
        timeoutGuided += timeoutTraining
    else: 
        timeTrainingEachGan = timeoutTraining

    ################ For 'yes' Training ################
    if(len(trainingDatasets[0]) != 0):
        dataDim = len(trainingDatasets[0][0])
        # Yes training
        configureTrainingYes(dataDim, trainingDatasets[0], pathResult, timeTrainingEachGan)
        existYesModel = True
    else:
        print_error_msj("A 'yes' training dataset could not be found")
        existYesModel = False
    
    ################ For 'no' Training ################
    if(len(trainingDatasets[1]) != 0):
        dataDim = len(trainingDatasets[1][0])
        configureTrainingNo(dataDim, trainingDatasets[1], pathResult, timeTrainingEachGan)
        existNoModel = True
    else:
        print_error_msj("A 'no' training dataset could not be found")
        existNoModel = False

    # El tiempo de entrenamiento fué menor que el parámetro recibido
    # el restante se lo paso al tiempo para el sampleo guiado
    #restTime = time.time() - initialTime
    #timeoutGuided += restTime
    
    #signal.alarm(0)
    trainingAndGenTime.append(time.time() - initialTime) # Time to training

def analyzeWorld(world, literal):
    global results, uniquesWorlds, uniquePrograms
    y = tuple(world)
    if(not y in uniquesWorlds):
        uniquesWorlds.add(y)
        newV = [1 - val for val in world]
        aux = ' '.join(str(x) for x in newV)
        t = aux.replace(" ","")
        worldId = int(t,2)
        # Build the PreDeLP Program for a world
        delpProgram = mapWorldToProgram(globalProgram, predicates, world)
        status = queryToProgram(delpProgram, literal, uniquePrograms)
        if status[1] == 'yes':
                results['yW'] += 1
                results['prY'] = results['prY'] + allWorlds[worldId]['prob']
        elif status[1] == 'no':
                results['nW'] += 1
                results['prN'] = results['prN'] + allWorlds[worldId]['prob']
        elif status[1] == 'undecided':
                results['undW'] += 1
                results['prUnd'] = results['prUnd'] + allWorlds[worldId]['prob']
        elif status[1] == 'unknown':
                results['unkW'] += 1
                results['prUnk'] = results['prUnk'] + allWorlds[worldId]['prob']

def samplingGan(pathResult, literal, timeoutGuided):
    global uniquesWorlds, uniquePrograms, world_data, results

    if(existYesModel):
        new_modelYes = tf.keras.models.load_model(pathResult + 'my_model_yes/')
    if(existNoModel):
        new_modelNo = tf.keras.models.load_model(pathResult + 'my_model_no/')
    # print("Unique worlds before gan -> " + str(len(uniquesWorlds)))
    # print("Unique programs befores gan -> " + str(len(uniquePrograms)))
    dataDim = len(predicates)    
    maxWorldsToAnalyze = int(numberOfWorlds/2)
    signal.signal(signal.SIGALRM, handlerTimer)
    print_ok_ops("\nTime setting (Guided): " + str(timeoutGuided) + " seconds")
    print_info_msj("Starting guided sampling")
    bar = IncrementalBar('Processing programs...', max=maxWorldsToAnalyze)
    initialTime = time.time()
    
    # For 'yes' worlds
    signal.alarm(int(timeoutGuided/2))
    try:
        for iAux1 in range(maxWorldsToAnalyze):
            noise = tf.random.uniform([1, dataDim]) # Controlar esto de normal o uniforme
            if existYesModel:
                #print("for 'yes'")
                modelsYes = new_modelYes(noise, training=False)
                modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
                listModelYes = modelsToBinYes[0].tolist()
            else:
                worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
                world = allWorlds[worldRandomId]
                listModelYes = world['program']
            
            analyzeWorld(listModelYes, literal)
                
            world_data += 1
            bar.next()
        bar.finish()
    except Exception as e:
        print('\n')
        print_error_msj(e)
        
    signal.alarm(0)

    # For 'no' Worlds
    bar = IncrementalBar('Processing programs...', max=maxWorldsToAnalyze)
    signal.alarm(int(timeoutGuided/2))
    try:
        for iAux2 in range(maxWorldsToAnalyze):
            noise = tf.random.uniform([1, dataDim]) # Controlar esto de normal o uniforme
            if existNoModel:
                modelsNo = new_modelNo(noise, training=False)
                modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
                listModelNo = modelsToBinNo[0].tolist()
            else:
                worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
                world = allWorlds[worldRandomId]
                listModelNo = world['program']
           
            analyzeWorld(listModelNo, literal)

            world_data += 1
            bar.next()
        bar.finish()
    except Exception as e:
        print('\n')
        print_error_msj(e)
        signal.alarm(0)

    signal.alarm(0)

    # print("Unique worlds after gan -> " + str(len(uniquesWorlds)))
    # print("Unique programs after gan -> " + str(len(uniquePrograms)))
    # print("yes Worlds: " + str(results['yW']))
    # print("no Worlds: " + str(results['nW']))
    # print("Undecided Worlds: " + str(results['undW']))
    # print("Total worlds analyzed: " + str(world_data))
    
    # To save the guided sampling time execution (trainingAndGenTime[2])
    trainingAndGenTime.append(time.time() - initialTime)
    results['l'] = results['prY']
    results['u'] = results['u'] - results['prN']
    results['timeExecution'] = trainingAndGenTime
    results['worldsAnalyzed'] = world_data
    with open(pathResult + 'timeGanResults.json', 'w') as outfile:  
        json.dump(results, outfile, indent=4)

def main(literal, dbName, timeoutSampling, timeoutTraining, timeoutGuidedRec, pathResult):
    global allWorlds, globalProgram, predicates, numberOfWorlds, timeoutGuided
    
    connectDB(dbName)
    print("Loading from db...")
    allWorlds = getAllWorlds()
    print("Worlds loaded")
    globalProgram = getAf()
    predicates = getEM()
    numberOfWorlds = len(allWorlds)
    timeoutGuided = timeoutGuidedRec
    # Sampling to find the dataset for training the GAN's models.
    # Traing the models
    samplingAndTraining(literal, timeoutSampling, timeoutTraining, pathResult)
    # Guided sampling with GAN's models or random worlds (if gans models can't be created)
    samplingGan(pathResult, literal, timeoutGuided)

# For arguments
parser = argparse.ArgumentParser(description="Script to perform the build and training of the GAN")

parser.add_argument('-l',
                    help = 'The literal to search the training dataset',
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
                    help='Path to save the results',
                    dest='pathResult',
                    required=True)
parser.add_argument('-ts',
                    help='Seconds to sampling',
                    dest='timeoutSampling',
                    type=int,
                    required=True)
parser.add_argument('-tt',
                    help='Seconds to training',
                    dest='timeoutTraining',
                    type=int,
                    required=True),
parser.add_argument('-tg',
                    help='Seconds to guided sampling',
                    dest='timeoutGuided',
                    type=int,
                    required=True)
arguments = parser.parse_args()

# Main
main(arguments.literal, arguments.dbName, arguments.timeoutSampling, arguments.timeoutTraining, arguments.timeoutGuided,arguments.pathResult)

