
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import numpy as np
import signal
from tensorflow.keras import layers
import time
from bnCode import *
from progress.spinner import Spinner
from datasets import *
from buildYesGAN import *
from buildNoGAN import *
tf.get_logger().setLevel('ERROR')
tf.get_logger().warning('test')

existYesModel, existNoModel = False, False
uniquesWorlds, uniquePrograms = set(), set()
globalProgram, predicates, numberOfWorlds = '', '', ''
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

def handlerTimer(signum, frame):
    raise Exception("Time over")

def searchTrainDataset(literal, timeout, pathResult):
    global results, uniquesWorlds, uniquePrograms
    worldsAnalyzed = 0
    datasetYes, datasetNo = [], []
   
    signal.signal(signal.SIGALRM, handlerTimer)
    print_error_msj("\nTime setting (Sampling): " + str(timeout) + " seconds")
    print_ok_ops('Starting random sampling...')
    
    #bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    spinner = Spinner('Processing worlds...')
    initialTime = time.time()
    signal.alarm(timeout)
    try:
        while(True):
            allWorlds = genSamples(bayesianNetwork, 10000, pathResult)
            for i in range(len(allWorlds)):
                worldData = allWorlds[i]
                worldAsTuple = tuple(worldData[0])
                if(not worldAsTuple in uniquesWorlds):
                    uniquesWorlds.add(worldAsTuple)
                    world = worldData[0]
                    evidence = worldData[1]
                    prWorld = getSamplingProb(evidence)
                    # Build the PreDeLP Program for a world
                    delpProgram = mapWorldToProgram(globalProgram, predicates, world)
                    status = queryToProgram(delpProgram, literal, uniquePrograms)
                    if status[1] == 'yes':
                        results['yes']['total'] += 1
                        results['yes']['prob'] = results['yes']['prob'] + prWorld
                        datasetYes.append(world)
                    elif status[1] == 'no':
                        results['no']['total'] += 1
                        results['no']['prob'] = results['no']['prob'] + prWorld
                        datasetNo.append(world)
                    elif status[1] == 'undecided':
                        results['und']['total'] += 1
                        results['und']['prob'] = results['und']['prob'] + prWorld
                    elif status[1] == 'unknown':
                        results['unk']['total'] += 1
                        results['unk']['prob'] = results['unk']['prob'] + prWorld
                spinner.next()
                worldsAnalyzed += 1
            #bar.finish()
    except Exception as e:
        print('\n')
        print_error_msj(e)
        
    signal.alarm(0)
    results['timeExecution'].append(time.time() - initialTime) # Time to sampling for find traininig dataset
    results['worldsAnalyzed'] = worldsAnalyzed
    print_ok_ops('Length of training data set found (Yes): %s' % (len(datasetYes)))
    print_ok_ops('Length of training data set found (No): %s' % (len(datasetNo)))
    # Save the training dataset finded
    #saveTrainingDataset(dataset, literalStatus)
    return [datasetYes, datasetNo]
    
def samplingAndTraining(literal, timeoutSampling, timeoutTraining, pathResult):
    global existNoModel, existYesModel, timeoutGuided

    # Search a training dataset
    # trainingDatasetes[0] = 'yes'
    # trainingDatasetes[1] = 'no'
    trainingDatasets = searchTrainDataset(literal, timeoutSampling, pathResult)
    
    print_error_msj("\nTime setting (Training): " + str(timeoutTraining) + " seconds")
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
    
    results['timeExecution'].append(time.time() - initialTime) # Time to training

def analyzeWorld(world, literal):
    global results, uniquesWorlds, uniquePrograms
    y = tuple(world)
    if(not y in uniquesWorlds):
        uniquesWorlds.add(y)
        evidence = { i : world[i] for i in range(0, len(world) ) } #Dict
        prWorld = getSamplingProb(evidence)
        # Build the PreDeLP Program for a world
        delpProgram = mapWorldToProgram(globalProgram, predicates, world)
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

def samplingGan(pathResult, literal, timeoutGuided):
    global results
    dim = len(predicates)
    world_data = 0

    if(existYesModel):
        new_modelYes = tf.keras.models.load_model(pathResult + 'my_model_yes/')
    if(existNoModel):
        new_modelNo = tf.keras.models.load_model(pathResult + 'my_model_no/')

    dataDim = len(predicates)    
    maxWorldsToAnalyze = int(numberOfWorlds/2)
    signal.signal(signal.SIGALRM, handlerTimer)
    print_error_msj("\nTime setting (Guided): " + str(timeoutGuided) + " seconds")
    print_ok_ops("Starting guided sampling")
    initialTime = time.time()
    
    # For 'yes' worlds
    #bar = IncrementalBar('Processing "yes" generated programs...', max=maxWorldsToAnalyze)
    signal.alarm(int(timeoutGuided/2))
    try:
        if(existYesModel):
            spinner = Spinner('Processing "yes" worlds...')
            while(True):
                noise = tf.random.normal([1, dataDim]) # Controlar esto de normal o uniforme
                #'YES' Models
                modelsYes = new_modelYes(noise, training=False)
                modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
                listModelYes = modelsToBinYes[0].tolist()
                analyzeWorld(listModelYes, literal)
                world_data += 1
                spinner.next()
            #bar.finish()
        else:
            spinner = Spinner('Processing random (yes time) worlds...')
            while(True):
                randomNm = np.random.randint(numberOfWorlds, size=1)[0]
                worldData = int_to_bin_with_format(randomNm, dim)
                listModelYes = worldData[0]
                analyzeWorld(listModelYes, literal)
                world_data += 1
                spinner.next()
            #bar.finish()
        # for iAux1 in range(maxWorldsToAnalyze):
        #     noise = tf.random.uniform([1, dataDim]) # Controlar esto de normal o uniforme
        #     if existYesModel:
        #         #print("for 'yes'")
        #         modelsYes = new_modelYes(noise, training=False)
        #         modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
        #         listModelYes = modelsToBinYes[0].tolist()
        #     else:
        #         worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
        #         world = allWorlds[worldRandomId]
        #         listModelYes = world['program']
            
        #     analyzeWorld(listModelYes, literal)
                
        #     world_data += 1
        #     bar.next()
        # bar.finish()
    except Exception as e:
        print('\n')
        print_error_msj(e)
        
    signal.alarm(0)

    # For 'no' Worlds
    #bar = IncrementalBar('Processing "no" generated programs...', max=maxWorldsToAnalyze)
    signal.alarm(int(timeoutGuided/2))
    try:
        if(existNoModel):
            spinner = Spinner('Processing "no" worlds...')
            while(True):
                noise = tf.random.normal([1, dataDim]) # Controlar esto de normal o uniforme
                #'NO' Models
                modelsNo = new_modelNo(noise, training=False)
                modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
                listModelNo = modelsToBinNo[0].tolist()
                analyzeWorld(listModelNo, literal)
                world_data += 1
                spinner.next()
            #bar.finish()
        else:
            spinner = Spinner('Processing random (no time) worlds...')
            while(True):
                randomNm = np.random.randint(numberOfWorlds, size=1)[0]
                worldData = int_to_bin_with_format(randomNm, dim)
                listModelNo = worldData[0]
                analyzeWorld(listModelNo, literal)
                world_data += 1
                spinner.next()
            #bar.finish()
        # for iAux2 in range(maxWorldsToAnalyze):
        #     noise = tf.random.uniform([1, dataDim]) # Controlar esto de normal o uniforme
        #     if existNoModel:
        #         modelsNo = new_modelNo(noise, training=False)
        #         modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
        #         listModelNo = modelsToBinNo[0].tolist()
        #     else:
        #         worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
        #         world = allWorlds[worldRandomId]
        #         listModelNo = world['program']
           
        #     analyzeWorld(listModelNo, literal)

        #     world_data += 1
        #     bar.next()
        # bar.finish()
    except Exception as e:
        print('\n')
        print_error_msj(e)

    signal.alarm(0)
    
    results['timeExecution'].append(time.time() - initialTime) #Time for guided sampling
    results['worldsAnalyzed'] += world_data
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']

    with open(pathResult + 'timeGanResults.json', 'w') as outfile:  
        json.dump(results, outfile, indent=4)

    #print results
    print_ok_ops("Results: ")
    print("Unique worlds: ", end='')
    print_ok_ops("%s" % (len(uniquesWorlds)))
    print("Unique programs: ", end='')
    print_ok_ops("%s" % (len(uniquePrograms)))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))

def main(literal, models, bn, timeoutSampling, timeoutTraining, timeoutGuidedRec, pathResult):
    global bayesianNetwork, globalProgram, predicates, timeoutGuided, numberOfWorlds
    
    bayesianNetwork = bn
    globalProgram = models["af"]
    predicates = models["randomVar"]
    numberOfWorlds = pow(2, len(predicates))
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
main(arguments.literal, arguments.program, arguments.bn, arguments.timeoutSampling, arguments.timeoutTraining, arguments.timeoutGuided,arguments.pathResult)

