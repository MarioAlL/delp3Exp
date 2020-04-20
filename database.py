import types
from utilsExp import *
from pymongo import MongoClient

client = MongoClient()
db = ''

def checkDB(database):
    global client
    dbnames = client.list_database_names()
    if database in dbnames:
        return True
    return False

def connectDB(database):
    global db
    global client
    db = client[database]

def closeDB():
    global client
    client.close()

def saveEm(predicates):
    global db
    collection = db.predicates
    data = {
        'predicates':predicates
    }
    result = collection.insert_one(data)
    if(result.acknowledged):
        return True
    else:
        return False

def saveAf(af):
    global db
    collection = db.af
    data = {
        'globalProgram':af
    }
    result = collection.insert_one(data)
    if(result.acknowledged):
        return True
    else:
        return False

def saveWorlds(worlds):
    global db
    collection = db.worlds
    result = collection.insert_many(worlds)
    if(result):
        return True
    else:
        return False

def getEM():
    global db
    collection = db.predicates
    aux = collection.find_one()
    em = aux['predicates']
    return em

def getAf():
    global db
    collection = db.af
    aux = collection.find_one()
    af = aux['globalProgram']
    return af

def getProgram():
    program = []
    af = getAf()
    
    for rule in af:
        program.append(rule[0])
    
    return program


def getWorldById(idWorld):
    id_World = int(idWorld)
    global db
    collection = db.worlds
    world = collection.find_one({'worldId' : id_World})
    return world
#    if not isinstance(world, types.NoneType):
#        return world
#    else:
#        print_error_msj("Error to load from db: World id: %s" % (idWorld))
#        exit()

def getIdsFromPrograms(programs):
    ids = []
    for program in programs:
        world = getWorldByProgram(program.tolist())
        ids.append(world["worldId"])
    return ids


# def getWorldByProgram(worldProgram):
#     global db
#     collection = db.worlds
#     world = collection.find_one({'program' : worldProgram})
#     return world

#Get the number of documents in a collection.
def getTrainingDatasetForDB(collection):
    global db
    trainingDataset = []
    cursor = db[collection].find({})
    for document in cursor:
        trainingDataset.append(document)
    return trainingDataset

def getProbabilitiesForDB():
    global db
    collection = db.probabilities
    result = collection.find_one('probabilities')
    if(result == None):
        return ''
    else:
        return result

def saveTrainingDataset(trainingDataset, literalStatus):
    global db
    training = db['training' + literalStatus[0]]
    datasetTraining = {
        'training':trainingDataset
    }
    result = training.insert_one(datasetTraining)
    if result.acknowledged:
        print("Training Dataset saved")

def saveProbabilities(probabilities):
    global db
    collection = db.probabilities
    probabilitiesValues = {
        'probabilities':probabilities
    }
    result = collection.insert_one(probabilitiesValues)
    if result.acknowledged:
        print("Probabilities saved")

def getAllWorlds():
    global db
    allWorlds = []
    worlds = db.worlds
    cursor = worlds.find({})
    for document in cursor:
        allWorlds.append(document)
    return allWorlds
