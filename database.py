import types
from utilsExp import *
from pymongo import MongoClient
from progress.spinner import Spinner

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


def getAllWorlds():
    global db
    allWorlds = []
    worlds = db.worlds
    cursor = worlds.find({})
    spinner = Spinner('Loading worlds from db...')
    for document in cursor:
        allWorlds.append(document)
        spinner.next()
    print_ok_ops("Completed")
    return allWorlds
