from termcolor import colored, cprint
import types
import sys
import time
import numpy as np
import json
from pysat.solvers import Glucose3
import itertools
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

def get_clause_for_solver(form, status):
    #form = Formula from the EM
    #status = True o False (if the formula has to be used or not)
    clause = []
    formAsList = form.strip().split(' ')
    if(len(formAsList) > 1):
        if status == True:
            if 'or' in formAsList:
                clause.append([int(formAsList[0]), int(formAsList[2])])
            else:
                #AND operator
                clause.append([int(formAsList[0])])
                clause.append([int(formAsList[2])])
        else:
            # Neg (convert to CNF)
            if 'or' in formAsList:
                clause.append([- int(formAsList[0])])
                clause.append([- int(formAsList[2])])
            else:
                clause.append([- int(formAsList[0]), - int(formAsList[2])])
        
        return clause
    else:
        if status == True:
            clause.append([int(form)])
            return clause
        else:
            clause.append([- int(form)])
            return clause

def get_worlds_by_program(formulas):
    clauseForSolver = []
    for i in formulas:
        clauseForSolver.append(get_clause_for_solver(i[0],i[1]))
    toSolve = list(itertools.chain.from_iterable(clauseForSolver))
    toReturn = []
    with Glucose3(bootstrap_with=toSolve) as g:
        for m in g.enum_models():
            toReturn.append(m)
    return toReturn

def getIsSatisfied(form, predicates, world):
    return eval(formatForm(form, predicates, world))


def mapBinToProgram(globalProgram, binArray):
    delpProgram = ''
    formsToChecks = []
    for i, binElem in enumerate(binArray):
        if globalProgram[i][1] != 'True':
            if binElem == 1:
                delpProgram += globalProgram[i][0]
                formsToChecks.append([globalProgram[i][1], True])
            else:
                formsToChecks.append([globalProgram[i][1], False])
    return [delpProgram, binArray, formsToChecks]


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
            #[[rules],[binary]]
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

def int_to_bin_with_format(number, lenght):
    toFormat = '{0:0'+str(lenght)+'b}'
    world = list(toFormat.format(int(number))) #List
    world = [int(value) for value in world]
    evidence = { i : world[i] for i in range(0, len(world) ) } #Dict
    return [world, evidence]

def getFormula(variables, probs):
    atoms = np.random.choice(variables, 2, replace=True)
    operator = np.random.choice(['and','or'], 1, replace=True)
    return str(atoms[0] + ' ' + operator[0] + ' ' + atoms[1])
# def getModels(pathToProgram):
#     file = open(pathFile,"r")
#     toDict = json.load(file)
#     predicates = toDict["randomVar"]
#     af = toDict["af"]
#     file.close()
#     return [predicates, af]