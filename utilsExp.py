from termcolor import colored, cprint
import types
import sys
import time
import numpy as np
from database import *
import json
#from consultDeLP import *


def print_info_msj(x): return cprint(x, 'grey', 'on_white')


def print_error_msj(x): return cprint(x, 'red')


def print_ok_ops(x): return cprint(x, 'green')


def getPos(predicate, predicates):
    if isinstance(predicate, types.IntType):
        # The predicate
        return predicates[predicate]
    else:
        # The position of the 'predicate' in the array 'predicates'
        return predicates.index(predicate)


def mapToPos(form, predicates):
    if '&' in form:
        atoms = form.split('&')
    elif '|' in form:
        atoms = form.split('|')
        return [getPos(atoms[0].strip(), predicates) + 1, getPos(atoms[1].strip(), predicates) + 1]
    else:
        return [getPos(form.strip(), predicates)]


def formatForm(form, predicates, world):
    aux = form.strip().split(' ')
    newForm = ''
    auxIndex = -1
    atomStatusInWorld = ''

    for element in aux:
        try:
            auxIndex = predicates.index(element)
            if world[auxIndex] == 1:
                atomStatusInWorld = "True"
            else:
                atomStatusInWorld = "False"
        except ValueError:
            atomStatusInWorld = element

        newForm = newForm + " " + atomStatusInWorld

    return newForm


def getIsSatisfied(form, predicates, world):
    #print(formatForm(form, predicates, world))
    # print eval(formatForm(form, predicates, world))
    return eval(formatForm(form, predicates, world))


def mapBinToProgram(rules, binArray):
    delpProgram = ''
    for i, binElem in enumerate(binArray):
        if binElem == 1:
            delpProgram += rules[i]
    return delpProgram


def mapWorldToProgram(globalProgram, em, world):
    delpProgram = ''
    delpProgramBin = []
    for rule in globalProgram:
        isSatisfied = getIsSatisfied(rule[1], em, world)
        if isSatisfied:
            delpProgram = delpProgram + rule[0]
            delpProgramBin.append(1)
        else:
            delpProgramBin.append(0)
    return [delpProgram, delpProgramBin]

def genProbabilities(numberOfWorlds):
    probabilities = []
    rnWorlds = []
    for i in range(numberOfWorlds):
        rnWorlds.append(np.random.randint(numberOfWorlds))
    #print("Rn: %s" % (rnWorlds))
    total = sum(rnWorlds)
    # print(total)
    for i in rnWorlds:
        probabilities.append(float(i)/total)
    #print("Prob: %s" % (probabilities))
    # print(sum(probabilities))
    return probabilities

def genNormalProbabilities(numberOfWorlds):
    mu, sigma = 1000, 1
    probabilities = []
    rnWorlds = []
    for i in range(numberOfWorlds):
        rnWorlds.append(np.random.normal(mu,sigma,1))
    #print("Rn: %s" % (rnWorlds))
    total = sum(rnWorlds)
    # print(total)
    for i in rnWorlds:
        probabilities.append(float(i)/float(total))
    #print("Prob: %s" % (probabilities))
    # print(sum(probabilities))
    return probabilities

def controlDBExist(dbName):
    if(not checkDB(dbName)):
        print_error_msj("Error: Database %s does not exist" % (dbName))
        exit()
    return dbName

def writeResult(results, times, pathFile):
    with open(pathFile + 'Results.json', 'w') as outfile:
        json.dump(results, outfile)
    with open(pathFile + 'Times.json', 'w') as outfile:
        json.dump(times, outfile)

def writeLebelledProgram(program, pathFile):
    with open(pathFile + '.json', 'w') as outfile:
        json.dump(program, outfile, indent=4)

def writeTimesGAN(results, pathFile, literalStatus):
    with open(pathFile + '/timesForTraining' + ''.join(map(str, literalStatus)) + '.json', 'w') as outfile:
        json.dump(results, outfile)

def getDataFromFile(pathFile):
    try:
        file = open(pathFile,"r")
        toDict = json.load(file)
        file.close()
        return toDict
    except IOError:
        #print(e)
        print_error_msj("Error trying to open the file: %s" % (pathFile))
        exit()
    except ValueError:
        #print(e)
        print_error_msj("JSON incorrect format: %s" % (pathFile))
        exit()
# if(sys.argv[1] == 'rnd'):
#     main(sys.argv[2], int(sys.argv[3]), sys.argv[4])
#     plt.plot(world_data, elapsed_data)
#     plt.ylabel('Time (seconds)')
#     plt.xlabel('Number of worlds')
#     plt.title('Random Sampling \n Pr(%s) = [%.4f, %.4f]' % (sys.argv[2], pYes, probTotal - pNo)) 
#     plt.tight_layout()
#     plt.savefig('random.pdf', bbox_inches='tight')
#     plt.show()
# elif(sys.argv[1] == 'exact'):
#     mainReal(sys.argv[2], sys.argv[3])
#     plt.plot(world_data, elapsed_data)
#     plt.ylabel('Time (seconds)')
#     plt.xlabel('Number of worlds')
#     plt.title('Total Sampling \n Pr(%s) = [%.4f, %.4f]' % (sys.argv[2], pYes, probTotal - pNo)) 
#     plt.tight_layout()
#     plt.savefig('Exact.pdf', bbox_inches='tight')
#     plt.show()
# else:
#     print('Error')
#     exit()
