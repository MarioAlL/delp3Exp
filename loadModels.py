import sys

import numpy as np
import itertools
from utilsExp import *
from pymongo import MongoClient
import argparse
import json
from database import *

def loadModels(data, dbName):
    print('Building and save worlds...')
    em = [var.strip() for var in data["randomVar"]]
    af = [[rule[0].strip() + ".", rule[1].strip()] for rule in list(data["af"])]
    
    # Building Worlds
    tuples = [] #To save the worlds
    valueTable = list(itertools.product([1, 0], repeat=len(em)))
    formatedValues =  list(map(list, valueTable))
    #probabilities = genProbabilities(len(formatedValues))
    probabilities = genNormalProbabilities(len(formatedValues))
    for windex, world in enumerate(formatedValues):
        tuples.append(dict(worldId=windex, program=world, prob=probabilities[windex]))

    # Save models
    connectDB(dbName)
    saveEmResult = saveEm(em)
    saveAfResult = saveAf(af)
    saveWorldsResult = saveWorlds(tuples)

    if saveEmResult and saveAfResult and saveWorldsResult:
        print_ok_ops("Models saved")
    else:
        print_error_msj("Error to save models")
    
    closeDB()  


    
parser = argparse.ArgumentParser(description = "Script to build and save models for the experiment")

parser.add_argument("-p", 
                    action="store", 
                    dest="data", 
                    help="The path to load the DeLP3E program",
                    type=getDataFromFile,
                    required=True)
parser.add_argument("-db",
                    action="store",
                    dest="dbName",
                    help="The database name to save the models",
                    required=True)
arguments = parser.parse_args()

loadModels(arguments.data, arguments.dbName)
