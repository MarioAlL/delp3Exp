import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import argparse
import tensorflow as tf
import numpy as np
from utilsExp import *
from consultDeLP import *
from database import *
import sys
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar

#plt.style.use('fivethirtyeight')
#world_data = []
#elapsed_data = []

def sampling(samples, literal, pathModel, pathResult):
    yW, nW, undW, unkW, empty = 0, 0, 0, 0, 0
    probY, probN, probUnd, probUnk, probEmpty = 0.00, 0.00, 0.00, 0.00, 0.00
    
    #To graph
    world_data = 0
    elapsed_data = 0
    timeExecution = []

    print("Generating models...")
    new_modelYes = tf.keras.models.load_model(pathModel + '_yes')
    new_modelNo = tf.keras.models.load_model(pathModel + '_no')
    # Check its architecture
    # new_model.summary()
    globalProgram = getAf()
    predicates = getEM()

    nSamples = int(samples)
    dataDim = len(predicates)
    noise = tf.random.normal([nSamples, dataDim]) # Controlar esto de normal o uniforme
    
    modelsYes = new_modelYes(noise, training=False)
    modelsNo = new_modelNo(noise, training=False)
    modelsToBinYes = (modelsYes.numpy() > 0.5) * 1
    modelsToBinNo = (modelsNo.numpy() > 0.5) * 1
    models = np.concatenate((modelsToBinYes, modelsToBinNo), axis=0)
    #uniquesWorlds = np.unique(modelsToBin, axis=0)
    generatedWorlds = getIdsFromPrograms(models)
    uniquesWorlds = []
    print_ok_ops("OK")
    uniquePrograms = [] # [[program],[status]]
    bar = IncrementalBar('Processing programs...', max=len(generatedWorlds))
    initialTime = time.time()
    worldsAnalyzed = 0
    for w in generatedWorlds:
        if(not w in uniquesWorlds):
            uniquesWorlds.append(w)
            world = getWorldById(w)
            #world = getWorldByProgram(uniqueWorld.tolist())
            # Build the PreDeLP Program for a world
            delpProgram = mapWorldToProgram(globalProgram, predicates, world['program'])
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status == 'yes':
                    yW += 1
                    probY = probY + world['prob']
            elif status == 'no':
                    nW += 1
                    probN = probN + world['prob']
            elif status == 'undecided':
                    undW += 1
                    probUnd = probUnd + world['prob']
            elif status == 'unknown':
                    unkW += 1
                    probUnk = probUnk + world['prob']

        world_data = worldsAnalyzed
        elapsed_data = time.time() - initialTime
        timeExecution.append([world_data, elapsed_data])
        worldsAnalyzed += 1
        
        bar.next()
    bar.finish()
    
    prob = [probY, 1.00 - probN]
    print_ok_ops("Results: ")
    print(len(uniquesWorlds))
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
        'experiment' : 'Gan'
    }
    times = {
        'timeExecution': timeExecution,
        'prob': [literal, prob[0], prob[1]],
        'experiment' : 'Gan'
    }
    writeResult(results, times, pathResult)


def main(literal, dbName, samples, pathResult, pathModel):
    connectDB(dbName)
    sampling(samples, literal, pathModel, pathResult)
    closeDB()

parser = argparse.ArgumentParser(description="Script to perform the GAN Sampling")

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
parser.add_argument('-pathM',
                    help='Path to load the GAN Model',
                    dest='pathModel',
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

main(arguments.literal, arguments.dbName, arguments.samples, arguments.pathResult, arguments.pathModel)