#import tensorflow as tf
from progress.bar import IncrementalBar
from pymongo import MongoClient
import numpy as np
from utilsExp import *
from database import *
from consultDeLP import *

# ###############################
# To show the architecture of the GAN
# ###############################


def getTrainingDataSet(data):
    bar = IncrementalBar('Building TEST Training Dataset', max=len(data))
    dataset = []
    for elem in data:
        if sum(elem) > 5:
            dataset.append(elem)
        bar.next()
    bar.finish()
    print("[TEST] - Training Dataset Dim: %s" % (len(dataset)))
    return dataset


def getTestDataSet(data):
    dataset = []
    for i, elem in enumerate(data):
        if sum(elem) > 5:
            dataset.append(1)
        else:
            dataset.append(0)
    return dataset


def getTestDataSetTEST(BATCH_SIZE, NOISE_DIM):
    noise = tf.random.uniform(shape=(BATCH_SIZE, NOISE_DIM),
                              minval=0,
                              maxval=2,
                              dtype=tf.dtypes.int32,
                              seed=None,
                              name=None)
    testDataSet = getTestDataSet(noise)
    return testDataSet


def getTrainingDatasetTEST(BATCH_SIZE, NOISE_DIM):
    noise = tf.random.uniform(shape=(BATCH_SIZE, NOISE_DIM),
                              minval=0,
                              maxval=2,
                              dtype=tf.dtypes.int32,
                              seed=None,
                              name=None)
    trainingDataSet = getTrainingDataSet(noise)
    return trainingDataSet
# ###############################
# ###############################

# ###############################
# To train GAN
# ###############################
def trainDataset(literal, database):
    connectDB(database)
    trainingDataSet = getTrainingDatasetForDB('training')
    if(len(trainingDataSet) == 0):
        dataset = []
        yWorlds = 0
        nWorlds = 0
        em = getEM()
        numberOfWorlds = pow(2, len(em))
        globalProgram = getAf()
        print_info_msj('Starting training dataset search...')
        bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
        for i in range(numberOfWorlds):
            worldRandomId = i
            tmpResult = getWorldById(int(worldRandomId))
            delpProgram = ''
            for rule in globalProgram:
                isSatisfied = getIsSatisfied(rule[1], em, tmpResult['program'])
                if isSatisfied:
                    delpProgram = delpProgram + rule[0]

            if(len(delpProgram) > 0):
                status = queryToProgram(delpProgram, literal)
                if status == 'yes':
                #   Yes
                    dataset.append(tmpResult['program'])
                    yWorlds += 1
                    #datalabels.append(1)
                # elif status == 'undecided':
                #     #Undecided
                #elif status == 'no':
                #     #no
                    #dataset.append(tmpResult['program'])
                    #nWorlds += 1
                    #datalabels.append(0)
                # elif status == 'unknown':
                #     #unknown
            
            bar.next()
        
        bar.finish()
        print_ok_ops('Length of training data set found: %s' % (len(dataset)))
        print_ok_ops('  Yes worlds: %s' % (yWorlds))
        #print_ok_ops('  No worlds: %s' % (nWorlds))
        saveTrainingDataset(dataset)
        return dataset
    else:
        print("Training Dataset loaded")
        return trainingDataSet[0]['training']



def getProbabilities(numberOfWorlds, database):
    connectDB(database)
    probabilitiesValues = getTrainingDatasetForDB('probabilities')
    if(len(probabilitiesValues) == 0):
        generate = genProbabilities(numberOfWorlds)
        saveProbabilities(generate)
        return generate
    else:
        print("Probabilities loaded")
        return probabilitiesValues[0]['probabilities']
# ###############################
# ###############################