
from __future__ import absolute_import, division, print_function, unicode_literals
import os
import argparse
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import numpy as np
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
# uniquePrograms = {(program),(status)}
uniquesWorlds, uniquePrograms = set(), set()
world_data = 0
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

def searchTrainDataset(literal, samples):
    global uniquePrograms, uniquesWorlds, results
    # If the training dataset exist
    #trainingDataSet = getTrainingDatasetForDB('training'+ literalStatus[0])
    datasetYes = []
    datasetNo = []
    print('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=samples)
    initialTime = time.time()
    for i in range(samples):
        worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
        world = allWorlds[worldRandomId]
        worldValues = tuple(world['program'])
        if(not worldValues in uniquesWorlds):
            uniquesWorlds.add(worldValues)
            # Build the PreDeLP Program for a world
            delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status[1] == 'yes':
                results['yes']['total'] += 1
                results['yes']['prob'] = results['yes']['prob'] + world['prob']
                datasetYes.append(world['program'])
            elif status[1] == 'no':
                results['no']['total'] += 1
                results['no']['prob'] = results['no']['prob'] + world['prob']
                datasetNo.append(world['program'])
            elif status[1] == 'undecided':
                results['und']['total'] += 1
                results['und']['prob'] = results['und']['prob'] + world['prob']
            elif status[1] == 'unknown':
                results['unk']['total'] += 1
                results['unk']['prob'] = results['unk']['prob'] + world['prob']
        bar.next()
    bar.finish()
    results['timeExecution'].append(time.time() - initialTime) # Time to sampling for find traininig dataset
    results['worldsAnalyzed'] = samples
    print_ok_ops('Length of training data set found (Yes): %s' % (len(datasetYes)))
    print_ok_ops('Length of training data set found (No): %s' % (len(datasetNo)))
    # Save the training dataset finded
    #saveTrainingDataset(dataset, literalStatus)
    return [datasetYes, datasetNo]

def samplingAndTraining(literal, samples, pathResult):
    global existNoModel, existYesModel, results

    # Search a training dataset
    trainingDatasets = searchTrainDataset(literal, samples)
    timeout = 0
    initialTime = time.time()
    if(len(trainingDatasets[0]) != 0):
        dataDim = len(trainingDatasets[0][0])
        # Yes training
        # trainingDatasetes[0] = 'yes'
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
            results['yes']['total'] += 1
            results['yes']['prob'] = results['yes']['prob'] + allWorlds[worldId]['prob']
        elif status[1] == 'no':
            results['no']['total'] += 1
            results['no']['prob'] = results['no']['prob'] + allWorlds[worldId]['prob']
        elif status[1] == 'undecided':
            results['und']['total'] += 1
            results['und']['prob'] = results['und']['prob'] + allWorlds[worldId]['prob']
        elif status[1] == 'unknown':
            results['unk']['total'] += 1
            results['unk']['prob'] = results['unk']['prob'] + allWorlds[worldId]['prob']

def samplingGan(samples, pathResult, literal):
    global results
    print_info_msj("Starting GAN Sampling...")

    nSamples = int(samples)
    initialTime = time.time()
    # Check if models exists 
    if existYesModel or existNoModel:
        dataDim = len(predicates)
        noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
        if existYesModel:
            new_modelYes = tf.keras.models.load_model(pathResult + 'my_model_yes/')
            modelsYes = new_modelYes(noise, training=False)
            modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
            listModelYes = [model.tolist() for model in modelsToBinYes]
        else:
            listModelYes = [world['program'] for world in np.random.choice(allWorlds, samples, replace=True)] # Con repeticiones
        
        noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
        if existNoModel:
            new_modelNo = tf.keras.models.load_model(pathResult + 'my_model_no/')
            modelsNo = new_modelNo(noise, training=False)
            modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
            listModelNo = [model.tolist() for model in modelsToBinNo]
        else:
            listModelNo = [world['program'] for world in np.random.choice(allWorlds, samples, replace=True)]
        
        models = listModelYes + listModelNo
    else:
        models = [world['program'] for world in np.random.choice(allWorlds, int(nSamples * 2), replace=True)] 
    
    print("Unique worlds before gan sampling --> %s" % (len(uniquesWorlds)))
    print("Unique programs before gan sampling --> %s" % (len(uniquePrograms)))
    
    bar = IncrementalBar('Processing programs...', max=len(models))
    for wAux in models:
        analyzeWorld(wAux, literal)
        bar.next()
    bar.finish()
    
    print("Unique worlds after gan -> " + str(len(uniquesWorlds)))
    print("Unique programs after gan -> " + str(len(uniquePrograms)))
    # print("yes Worlds: " + str(results['yW']))
    # print("no Worlds: " + str(results['nW']))
    # print("Undecided Worlds: " + str(results['undW']))
    # print("Total worlds analyzed: " + str(world_data))
    
    results['timeExecution'].append(time.time() - initialTime)
    results['worldsAnalyzed'] += nSamples*2
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']

    with open(pathResult + 'sampleGanResults.json', 'w') as outfile:  
        json.dump(results, outfile, indent=4)

def main(literal, dbName, st, ss, pathResult):
    global allWorlds, globalProgram, predicates, numberOfWorlds
    
    connectDB(dbName)
    print("Loading from db...")
    allWorlds = getAllWorlds()
    print("Worlds loaded")
    globalProgram = getAf()
    predicates = getEM()
    numberOfWorlds = len(allWorlds)

    # Sampling and Training
    samplingAndTraining(literal, st, pathResult)
    # Guiaded Sampling
    samplingGan(int(ss/2), pathResult, literal)


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
parser.add_argument('-st',
                    help='Number of samples to search a training dataset',
                    dest='samplesT',
                    type=int,
                    required=True)
parser.add_argument('-ss',
                    help='Number of samples',
                    dest='samplesS',
                    type=int,
                    required=True)
arguments = parser.parse_args()

main(arguments.literal, arguments.dbName, arguments.samplesT, arguments.samplesS, arguments.pathResult)

