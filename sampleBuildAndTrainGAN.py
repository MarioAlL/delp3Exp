from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import numpy as np
from tensorflow.keras import layers
import time
from bnCode import *
from progress.bar import IncrementalBar
from datasets import *
from buildYesGAN import *
from buildNoGAN import *
tf.get_logger().setLevel('ERROR')
tf.get_logger().warning('test')


existYesModel, existNoModel = False, False
uniquesWorlds, uniquePrograms = set(), set()
bayesianNetworl, allWorlds, globalProgram, predicates = '', '', '', ''
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

def searchTrainDataset(literal):
    global uniquePrograms, uniquesWorlds, results
    numberOfWorlds = allWorlds
    dim = len(predicates)
    numberOfAllWorlds = pow(2, dim)
    # If the training dataset exist
    #trainingDataSet = getTrainingDatasetForDB('training'+ literalStatus[0])
    datasetYes = []
    datasetNo = []
    print_ok_ops('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    initialTime = time.time()
    for i in range(numberOfWorlds):
        randomNum = np.random.choice(numberOfAllWorlds,1)
        worldData = int_to_bin_with_format(randomNum[0], dim)
        #worldData = allWorlds[i]
        worldAsTuple = tuple(worldData[0])
        if(not worldAsTuple in uniquesWorlds):
            uniquesWorlds.add(worldAsTuple)
            world = worldData[0]
            evidence = worldData[1]
            prWorld = getSamplingProb(evidence)
            # Build the PreDeLP Program for a world
            # delpProgram = [[rules], [binary]]
            delpProgram = mapWorldToProgram(globalProgram, predicates, world)
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status[1] == 'yes':
                results['yes']['total'] += 1
                results['yes']['prob'] = results['yes']['prob'] + prWorld
                datasetYes.append(delpProgram[1])
            elif status[1] == 'no':
                results['no']['total'] += 1
                results['no']['prob'] = results['no']['prob'] + prWorld
                datasetNo.append(delpProgram[1])
            elif status[1] == 'undecided':
                results['und']['total'] += 1
                results['und']['prob'] = results['und']['prob'] + prWorld
            elif status[1] == 'unknown':
                results['unk']['total'] += 1
                results['unk']['prob'] = results['unk']['prob'] + prWorld
        bar.next()
    bar.finish()
    results['timeExecution'].append(time.time() - initialTime) # Time to sampling for find traininig dataset
    results['worldsAnalyzed'] = numberOfWorlds
    print_ok_ops('Length of training data set found (Yes): %s' % (len(datasetYes)))
    print_ok_ops('Length of training data set found (No): %s' % (len(datasetNo)))
    # Save the training dataset finded
    #saveTrainingDataset(dataset, literalStatus)
    return [datasetYes, datasetNo]

def samplingAndTraining(literal, pathResult):
    global existNoModel, existYesModel, results

    # Search a training dataset
    trainingDatasets = searchTrainDataset(literal)
    
    
    timeout = 0
    initialTime = time.time()
    if(len(trainingDatasets[0]) != 0):
        dataDim = len(trainingDatasets[0][0])
        # Yes training
        # trainingDatasetes[1] = 'no'
        configureTrainingYes(dataDim, trainingDatasets[0], pathResult, timeout)
        existYesModel = True
    else:
        print_error_msj("A 'yes' training dataset could not be found")
        existYesModel = False
    
    ################ For 'no' Training ################
    if(len(trainingDatasets[1]) != 0):
        dataDim = len(trainingDatasets[1][0])
        # No training
        # trainingDatasetes[1] = 'no'
        configureTrainingNo(dataDim, trainingDatasets[1], pathResult, timeout)
        existNoModel = True
    else:
        print_error_msj("A 'no' training dataset could not be found")
        existNoModel = False
   
    results['timeExecution'].append(time.time() - initialTime) # Time to training

def analyzeWorld(progInBin, literal):
    global results, uniquesWorlds, uniquePrograms
    
    # Build the PreDeLP Program from the program in binary
    delpProgram = mapBinToProgram(globalProgram, progInBin)
    status = queryToProgram(delpProgram, literal, uniquePrograms)
    if status[1] == 'yes':
        results['yes']['total'] += 1
        #results['yes']['prob'] = results['yes']['prob'] + prWorld
    elif status[1] == 'no':
        results['no']['total'] += 1
        #results['no']['prob'] = results['no']['prob'] + prWorld
    elif status[1] == 'undecided':
        results['und']['total'] += 1
        #results['und']['prob'] = results['und']['prob'] + prWorld
    elif status[1] == 'unknown':
        results['unk']['total'] += 1
        #results['unk']['prob'] = results['unk']['prob'] + prWorld

def samplingGan(samples, pathResult, literal):
    global results
    newYesWorldsGenerated = results["yes"]['total']
    newNoWorldsGenerated = results["no"]['total']

    print_error_msj("Starting GAN Sampling...")

    nSamples = int(samples)
    initialTime = time.time()
    # Check if models exists 
    if existYesModel or existNoModel:
        dataDim = len(globalProgram)
        noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
        if existYesModel:
            new_modelYes = tf.keras.models.load_model(pathResult + 'my_model_yes/')
            modelsYes = new_modelYes(noise, training=False)
            modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
            listModelYes = [model.tolist() for model in modelsToBinYes]
        else:
            listModelYes = [world for [world, asDict] in genSamples(bayesianNetwork, nSamples, pathResult)]
        
        noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
        if existNoModel:
            new_modelNo = tf.keras.models.load_model(pathResult + 'my_model_no/')
            modelsNo = new_modelNo(noise, training=False)
            modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
            listModelNo = [model.tolist() for model in modelsToBinNo]
        else:
            listModelNo = [world for [world, asDict] in genSamples(bayesianNetwork, nSamples, pathResult)]
        
        models = listModelYes + listModelNo
    else:
        models = [world['program'] for world in np.random.choice(allWorlds, int(nSamples * 2), replace=True)] 
    
    bar = IncrementalBar('Processing generated programs...', max=len(models))
    
    for wAux in models:
        analyzeWorld(wAux, literal)
        bar.next()
    bar.finish()
    
    results['timeExecution'].append(time.time() - initialTime)# Time for guided sampling
    results['worldsAnalyzed'] += nSamples*2
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']

    with open(pathResult + 'sampleGanResults.json', 'w') as outfile:  
        json.dump(results, outfile, indent=4)

    newYesWorldsGenerated = results["yes"]['total'] - newYesWorldsGenerated
    newNoWorldsGenerated = results["no"]['total'] - newNoWorldsGenerated
    print_error_msj("New yes worlds generated by GAN: %s" % (newYesWorldsGenerated))
    print_error_msj("New no worlds generated by GAN: %s" % (newNoWorldsGenerated))

    #print results
    print_ok_ops("Results: ")
    print("Unique worlds: ", end='')
    print_ok_ops("%s" % (len(uniquesWorlds)))
    print("Unique programs: ", end='')
    print_ok_ops("%s" % (len(uniquePrograms)))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))

def main(literal, models, bn, st, ss, pathResult):
    global allWorlds, globalProgram, predicates, numberOfWorlds, bayesianNetwork
    
    bayesianNetwork = bn
    allWorlds = st
    #allWorlds = genSamples(bn, st, pathResult)
    globalProgram = models["af"]
    predicates = models["randomVar"]

    # Sampling and Training
    samplingAndTraining(literal, pathResult)
    # Guiaded Sampling
    samplingGan(int(ss/2), pathResult, literal)


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
parser.add_argument('-st',
                    help='Number of samples to search a training dataset',
                    dest='samplesT',
                    type=int,
                    required=True)
parser.add_argument('-sg',
                    help='Number of guided samples',
                    dest='samplesS',
                    type=int,
                    required=True)
arguments = parser.parse_args()

main(arguments.literal, arguments.program, arguments.bn, arguments.samplesT, arguments.samplesS, arguments.pathResult)

