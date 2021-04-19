from termcolor import cprint
import types
import numpy as np
import json
#from pysat.solvers import Glucose3
import itertools
import matplotlib.pyplot as plt


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
    newForm = ''
    auxIndex = -1
    atomStatusInWorld = ''
    aux = form.strip().split(' ')
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


def get_clause_for_solver(clauses):
    toReturn = []
    toAnds = clauses.split("&")
    for elem in toAnds:
        if "|" in elem:
            toOrs = elem.split("|")
            toReturn.append([int(ors.replace("(", "").replace(")", "").strip()) for ors in toOrs])
        else:
            toReturn.append([int(elem.replace("(", "").replace(")", "").strip())])
    return toReturn


def completeWorlds(dim):
    valueTable = list(itertools.product([1, 0], repeat=dim))
    formatedValues = list(map(list, valueTable))
    return formatedValues


def get_worlds_by_program(clauses):
    clauseForSolver = []
    for clause in clauses:
        if clause != '$':
            clauseForSolver.append(get_clause_for_solver(clause))
    toSolve = list(itertools.chain.from_iterable(clauseForSolver))
    toReturn = []
    with Glucose3(bootstrap_with=toSolve) as g:
        for m in g.enum_models():
            toReturn.append(m)
    return toReturn


def getIsSatisfied(form, predicates, world):
    return eval(formatForm(form, predicates, world))


def mapBinToProgram(globalProgram, binArray):
    evidence = {}
    delpProgram = ''
    for index, value in enumerate(globalProgram):
        if value[1].isdigit() and not int(value[1]) in evidence:
            evidence[int(value[1])] = binArray[index]
            if binArray[index] == 1: delpProgram += value[0]
        elif value[1] == 'True':
            if binArray[index] == 1:
                delpProgram += value[0]
            else:
                return -1  # Incorrect Program
                break
        elif evidence[int(value[1])] != binArray[index]:
            return -1  # Inconsistent Program
            break
    return [delpProgram, binArray, evidence]


# print(mapBinToProgram([["a","1"],["b","True"],["c","3"],["d","3"]],[0,1,0,1]))

def map_world_to_program(globalProgram, em, world):
    delpProgram = ''
    delpProgramBin = []
    for rule in globalProgram:
        isSatisfied = getIsSatisfied(rule[1], em, world)
        if isSatisfied:
            delpProgram = delpProgram + rule[0]
            delpProgramBin.append(1)
        else:
            delpProgramBin.append(0)
            # [[rules],[binary]]
    return [delpProgram, delpProgramBin]


def genProbabilities(numberOfWorlds):
    probabilities = []
    rnWorlds = []
    for i in range(numberOfWorlds):
        rnWorlds.append(np.random.randint(numberOfWorlds))
    # print("Rn: %s" % (rnWorlds))
    total = sum(rnWorlds)
    # print(total)
    for i in rnWorlds:
        probabilities.append(float(i) / total)
    # print("Prob: %s" % (probabilities))
    # print(sum(probabilities))
    return probabilities


def genNormalProbabilities(numberOfWorlds):
    mu, sigma = 1000, 1
    probabilities = []
    rnWorlds = []
    for i in range(numberOfWorlds):
        rnWorlds.append(np.random.normal(mu, sigma, 1))
    # print("Rn: %s" % (rnWorlds))
    total = sum(rnWorlds)
    # print(total)
    for i in rnWorlds:
        probabilities.append(float(i) / float(total))
    # print("Prob: %s" % (probabilities))
    # print(sum(probabilities))
    return probabilities


def writeResult(results, times, pathFile):
    with open(pathFile + 'Results.json', 'w') as outfile:
        json.dump(results, outfile)
    with open(pathFile + 'Times.json', 'w') as outfile:
        json.dump(times, outfile)


def write_json_file(content, path_file):
    with open(path_file + '.json', 'w') as outfile:
        json.dump(content, outfile, indent = 4)

def writeTimesGAN(results, pathFile, literalStatus):
    with open(pathFile + '/timesForTraining' + ''.join(map(str, literalStatus)) + '.json', 'w') as outfile:
        json.dump(results, outfile)


def getDataFromFile(pathFile):
    try:
        file = open(pathFile, "r")
        toDict = json.load(file)
        file.close()
        return toDict
    except IOError:
        # print(e)
        print_error_msj("Error trying to open the file: %s" % (pathFile))
        exit()
    except ValueError:
        # print(e)
        print_error_msj("JSON incorrect format: %s" % (pathFile))
        exit()


def int_to_bin_with_format(number, lenght):
    toFormat = '{0:0' + str(lenght) + 'b}'
    world = list(toFormat.format(int(number)))  # List
    world = [int(value) for value in world]
    evidence = {i: world[i] for i in range(0, len(world))}  # Dict
    return [world, evidence]


def save_unique_worlds(uniqueWorlds, exp, path):
    with open(path + exp + '.json', 'w') as outfile:
        binary = [''.join(str(x) for x in sample) for sample in uniqueWorlds]
        numbers = [int(elem, 2) for elem in binary]
        json.dump({'samples': numbers}, outfile)


def plot_samples(path):
    try:
        fileRandom = open(path + 'random.json', 'r')
        fileGAN = open(path + 'gan.json', 'r')
        toDictRandom = json.load(fileRandom)
        toDictGAN = json.load(fileGAN)
        fileRandom.close()
        fileGAN.close()

        data = [toDictRandom["samples"], toDictGAN["samples"]]
        plt.hist(data, alpha=0.6, bins=10, label=['Random', 'GAN'], color=['red', 'blue'])
        plt.legend()
        plt.show()
        # return [toDictRandom["samples"], toDictGAN["samples"]]
    except IOError:
        print_error_msj("Error trying to open the file: %s" % (path))
        exit()


