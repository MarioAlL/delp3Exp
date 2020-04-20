
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


existYesModel = False
existNoModel = False
uniquesWorlds = set() #Worlds Programs {(1,0,...,0),(1,0,...,0)}
uniquesWorldsIds = set() #Ids {(id),(id)}
uniquePrograms = set() # {(program),(status)}
elapsed_data = 0
world_data = 0
initialTime = 0
trainingAndGenTime = []
previousResults = []

def searchTrainDataset(literal, samples, allWorlds, pathResult, uniquesWorlds, uniquePrograms):
    # To control if the training dataset exist
    #trainingDataSet = getTrainingDatasetForDB('training'+ literalStatus[0])
    global elapsed_data
    global world_data
    global initialTime
    global previousResults
    trainingDataSet = []
    if(len(trainingDataSet) == 0):
        datasetYes = []
        datasetNo = []
        yW, nW, undW, unkW, empty = 0, 0, 0, 0, 0
        probY, probN, probUnd, probUnk, probEmpty = 0.00, 0.00, 0.00, 0.00, 0.00
        
        #To graph
        #world_data = 0
        #elapsed_data = 0
        timeExecution = []

        globalProgram = getAf()
        predicates = getEM()
        #numberOfWorlds = pow(2, len(predicates))
        numberOfWorlds = len(allWorlds)
        # print("Loading from db...")
        # allWorlds = getAllWorlds()
        # print("Worlds loaded")
        
        
        print('Starting random sampling...')
        bar = IncrementalBar('Processing worlds', max=samples)
        #worldsIds = np.random.choice(numberOfWorlds, samples, replace=False)
        initialTime = time.time()
        for i in range(samples):
            worldRandomId = np.random.randint(numberOfWorlds, size=1)[0]
            #worldRandomId = worldsIds[i]
            if(not worldRandomId in uniquesWorldsIds):
                world = allWorlds[worldRandomId]
                uniquesWorldsIds.add(worldRandomId)
                uniquesWorlds.add(tuple(world['program']))
                #world = getWorldById(0) # The binary array
                
                # Build the PreDeLP Program for a world
                delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
                status = queryToProgram(delpProgram, literal, uniquePrograms)
                if status[1] == 'yes':
                        yW += 1
                        probY = probY + world['prob']
                        datasetYes.append(world['program'])
                elif status[1] == 'no':
                        nW += 1
                        probN = probN + world['prob']
                        datasetNo.append(world['program'])
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
        prob = [probY, 1.00 - probN]
        print_ok_ops("Results: ")
        print("Unique worlds: %s" % (len(uniquesWorlds)))
        print("Unique programs: %s" % (len(uniquePrograms)))
        print("Yes worlds: \t\t %s \t\t\t Prob =  %.4f" % (yW, probY))
        print("No worlds: \t\t %s \t\t\t Prob =  %.4f" % (nW, probN))
        print("Undecided worlds: \t %s \t\t\t Prob =  %.4f" % (undW, probUnd))
        print("Unknow worlds: \t\t %s \t\t\t Prob =  %.4f" % (unkW, probUnk))
        print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, prob[0], prob[1]))
        
        #Here save file with result
        results = {
            'yW': yW,
            'probY': probY,
            'nW': nW,
            'probN': probN,
            'undW': undW,
            'probUnd': probUnd,
            'unkW': unkW,
            'probUnk': probUnk,
            'prob': [literal, prob[0], prob[1]],
            'experiment' : 'Random Sampling',
            'timeExecution': timeExecution[-1][1] # Total time
        }
        # times = {
        #     'timeExecution': timeExecution,
        #     #'prob': [literal, prob[0], prob[1]],
        #     'experiment' : 'Random Sampling'
        # }
        # writeResult(results, times, pathResult + 'training')
        previousResults.append(results)
        print_ok_ops('Length of training data set found (Yes): %s' % (len(datasetYes)))
        print_ok_ops('Length of training data set found (No): %s' % (len(datasetNo)))
        # Save the training dataset finded
        #saveTrainingDataset(dataset, literalStatus)
        #trainingAndGenTime.append(world_data)
        trainingAndGenTime.append(elapsed_data)

        return [datasetYes, datasetNo]
    else:
        print("Training Dataset loaded")
        return trainingDataSet[0]['training']


def main(literal, samples, pathResult, allWorlds):
    # global uniquesWorlds
    # global uniquePrograms
    global existNoModel
    global existYesModel
    global initialTime
    global world_data
    print_info_msj("Training")
    #initialTime = time.time()
    # Search a training dataset
    trainingDatasets = searchTrainDataset(literal, samples, allWorlds, pathResult, uniquesWorlds, uniquePrograms)
    #timeToFindTDS = time.time() - initialTime
    
    if(len(trainingDatasets[0]) != 0):
        dataDim = len(trainingDatasets[0][0])
        # Yes training
        # trainingDatasetes[0] = 'yes'
        # trainingDatasetes[1] = 'no'
        configureTrainingYes(dataDim, trainingDatasets[0], initialTime, pathResult, world_data, elapsed_data)
        existYesModel = True
        
    else:
        print_error_msj("A 'yes' training dataset could not be found")
        existYesModel = False
    
    ################ For 'no' Training ################
    if(len(trainingDatasets[1]) != 0):
        dataDim = len(trainingDatasets[1][0])
        configureTrainingNo(dataDim, trainingDatasets[1], initialTime, pathResult,  world_data, elapsed_data)
        existNoModel = True
    else:
        print_error_msj("A 'no' training dataset could not be found")
        existNoModel = False
    
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

def samplingGan(allWorlds, samples, pathResult, literal):
    # global uniquesWorlds
    # global uniquePrograms
    global elapsed_data
    global world_data
    global initialTime
    global previousResults
    print_info_msj("Sampling")
    yW, nW, undW, unkW, empty = previousResults[0]['yW'], previousResults[0]['nW'], previousResults[0]['undW'], previousResults[0]['unkW'], 0
    probY, probN, probUnd, probUnk, probEmpty = previousResults[0]['probY'], previousResults[0]['probN'], 0.00, 0.00, 0.00
    #To graph
    #world_data = 0
    #elapsed_data = 0
    timeExecution = []
    globalProgram = getAf()
    predicates = getEM()
    
    nSamples = int(samples)
    # Check if models exists 
    if existYesModel or existNoModel:
        print("Generating models...")
        dataDim = len(predicates)
        noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
        if existYesModel:
            print("for 'yes'")
            new_modelYes = tf.keras.models.load_model('exp/my_model_yes/')
            modelsYes = new_modelYes(noise, training=False)
            modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
            listModelYes = [model.tolist() for model in modelsToBinYes]
        else:
            listModelYes = [world['program'] for world in np.random.choice(allWorlds, samples, replace=True)] # Con repeticiones
        if existNoModel:
            print("for 'no'")
            new_modelNo = tf.keras.models.load_model('exp/my_model_no/')
            modelsNo = new_modelNo(noise, training=False)
            modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
            listModelNo = [model.tolist() for model in modelsToBinNo]
        else:
            listModelNo = [world['program'] for world in np.random.choice(allWorlds, samples, replace=True)]
        
        models = listModelYes + listModelNo
    else:
        models = [world['program'] for world in np.random.choice(allWorlds, samples * 2, replace=True)] 
    
 
    #uniquesWorlds = np.unique(modelsToBin, axis=0)
    #generatedWorlds = getIdsFromPrograms(models)
    #uniquesWorlds = []
    print_ok_ops("OK")
    #uniquePrograms = [] # [[program],[status]]
    print("Before gan sampling --> %s" % (len(uniquesWorlds)))
    print("Before gan sampling --> %s" % (len(uniquePrograms)))
    # setOfWolrds = set()
    # for i in uniquesWorlds:
    #     setOfWolrds.add(tuple(i))
    
    bar = IncrementalBar('Processing programs...', max=len(models))
    #initialTime = time.time()
    
    trainingAndGenTime.append((time.time() - initialTime) - trainingAndGenTime[0])
    
    for wAux in models:
        y = tuple(wAux)
        if(not y in uniquesWorlds):
            uniquesWorlds.add(y)
            
            newV = [1 - val for val in wAux]
            aux = ' '.join(str(x) for x in newV)
            t = aux.replace(" ","")
            worldId = int(t,2)
            
            #uniquesWorldsIds.append(wAux)
            #world = next((item for item in allWorlds if item['program'] == wAux), None)
            #world = getWorldByProgram(uniqueWorld.tolist())
            # Build the PreDeLP Program for a world
            delpProgram = mapWorldToProgram(globalProgram, predicates, wAux)
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status[1] == 'yes':
                    yW += 1
                    #world = next((item for item in allWorlds if item['program'] == wAux), None)
                    #probY = probY + world['prob']
                    probY = probY + allWorlds[worldId]['prob']
                    #probY = 1.00
            elif status[1] == 'no':
                    nW += 1
                    #world = next((item for item in allWorlds if item['program'] == wAux), None)
                    #probN = probN + world['prob']
                    probN = probN + allWorlds[worldId]['prob']
                    #probN = 1.00
            elif status[1] == 'undecided':
                    undW += 1
                    #probUnd = probUnd + world['prob']
                    probUnd = probUnd + 0.00
            elif status[1] == 'unknown':
                    unkW += 1
                    #probUnk = probUnk + world['prob']
                    probUnk = probUnk + 0.00

        world_data += 1
        elapsed_data = time.time() - initialTime
        timeExecution.append([world_data, elapsed_data])
        
        
        bar.next()
    bar.finish()
    trainingAndGenTime.append((time.time() - initialTime) - trainingAndGenTime[0] - trainingAndGenTime[1])
    prob = [probY, 1.00 - probN]
    print_ok_ops("Results: ")
    print("Unique worlds: %s" % (len(uniquesWorlds)))
    print("Unique programs: %s" % (len(uniquePrograms)))
    print("Yes worlds: \t\t %s \t\t\t Prob =  %.4f" % (yW, probY))
    print("No worlds: \t\t %s \t\t\t Prob =  %.4f" % (nW, probN))
    print("Undecided worlds: \t %s \t\t\t Prob =  %.4f" % (undW, probUnd))
    print("Unknow worlds: \t\t %s \t\t\t Prob =  %.4f" % (unkW, probUnk))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, prob[0], prob[1]))
    
    times = {
        'timeExecution': trainingAndGenTime,
        'experiment': 'Gan',
        'prob':[literal, prob[0], prob[1]]
    }
    with open(pathResult + 'ganResults.json', 'w') as outfile:
        json.dump(times, outfile)
    #Here save file with result
    # results = {
    #     'yW': yW,
    #     'probY': probY,
    #     'nW': nW,
    #     'probN': probN,
    #     'undW': undW,
    #     'probUnd': probUnd,
    #     'unkW': unkW,
    #     'probUnk': probUnk,
    #     'prob': [literal, prob[0], prob[1]],
    #     'experiment' : 'Gan Sampling',
    #     'timeExecution': timeExecution[-1][1] # Total time
    # }
    # times = {
    #     'timeExecution': timeExecution,
    #     'prob': [literal, prob[0], prob[1]],
    #     'experiment' : 'Gan Sampling'
    # }
    # writeResult(results, times, pathResult + 'sampling')
    
def showResults():
    global trainingAndGenTime
    # print(trainingAndGenTime)
    # rest = int(trainingAndGenTime[2] - trainingAndGenTime[1])
    # start = trainingAndGenTime[1]
    # timeExecution = []
    # for i in range(rest):
    #     start += 1
    #     timeExecution.append([trainingAndGenTime[0], start])
    #timeExecution = [[trainingAndGenTime[0], trainingAndGenTime[1]], [trainingAndGenTime[0], trainingAndGenTime[2]]]
    times = {
        'timeExecution': trainingAndGenTime,
        'experiment': 'Gan'
    }
    with open('ganResults.json', 'w') as outfile:
        json.dump(times, outfile)

def startTraining(literal, dbName, st, ss, pathResult):
    connectDB(dbName)
    print("Loading from db...")
    allWorlds = getAllWorlds()
    print("Worlds loaded")

    main(literal, st, pathResult, allWorlds)

    samplingGan(allWorlds, int(ss/2), pathResult, literal)
    
startTraining(arguments.literal, arguments.dbName, arguments.samplesT, arguments.samplesS, arguments.pathResult)


