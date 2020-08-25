import sys

from utilsExp import *
import argparse
import numpy as np
from em.bn import *
import pyAgrum as gum

def main(data, nvar, nvaruse, pathToSave):
    if(nvaruse <= nvar):
        af = []
        randomVar = [str(var + 1) for var in list(range(nvar))] # Generate variables
        rules = [rule[:-1] for rule in data["delp"][1:]]
        randomVarToUse = randomVar[:nvaruse] #Get the first nvaruse from randomVar
        
        randomVarToUse.append('True')
        #trueProb = [0.3]
        #otherValuesProb = [float(0.7) / float((len(randomVarToUse) - 1))] * (len(randomVarToUse) - 1)
        #probs = otherValuesProb + trueProb
        
        probs = []
        #print(randomVarToUse)
        #print(probs)
        for rule in rules:
            form = getForm(randomVarToUse, probs)
            af.append([rule+';', form])

        program = {
            "randomVar": randomVar,
            "varUsed": randomVarToUse,
            "af": af
        }

        writeLebelledProgram(program, pathToSave + 'models')# Save the DeLP3E program
        
        #For build a random Bayesian Network
        nodes = len(randomVar)
        myBN = BayesNetwork('TEST',pathToSave)
        myBN.build_save_random_BN(nodes, nodes, False)
        myBN.make_CPTs(myBN.structure[0], 0.9)
        #myBN.show_prob_dist(50000)
        #buildAndSaveBN(nodes, nodes, pathToSave)# Generate and save a random Bayesian Net
    else:
        print_error_msj("Error")
        exit()

def getForm(variables, probs):
    #form = np.random.choice(variables, 1, p = probs,replace=True)
    form = np.random.choice(variables, 1, replace=True)
    #neg = np.random.choice(["","~"], 1, replace=True)
    return str(form[0])

def getFormula(variables, probs):
    if(len(probs) > 0):
        atoms = np.random.choice(variables, 2, p= probs, replace=True)
    else:
        atoms = np.random.choice(variables, 2, replace=True)

    if 'True' in atoms:
        return 'True'
    else:
        operator = np.random.choice(['and','or'], 1, replace=True)
        return str(atoms[0] + ' ' + operator[0] + ' ' + atoms[1])


def checkNumberElems(nvar, nvaruse):
    if nvaruse > nvar:
        return True
    else:
        return False

# parser = argparse.ArgumentParser(description='Script to generate formulas randomly for a del3e program')
# parser.add_argument('-p',
#                     action='store',
#                     help="The delp3e program",
#                     dest="data",
#                     type=getDataFromFile,
#                     required=True)
# parser.add_argument('-nvar',
#                     help='Number of elements',
#                     dest="nvar",
#                     type=int,
#                     required=True)
# parser.add_argument('-nvaruse',
#                     help='Number of elements to use in each formula',
#                     dest="nvaruse",
#                     type=int,
#                     required=True)
# parser.add_argument('-op',
#                     help='Operator to use (NOT IMPLEMENTED)',
#                     dest="operators",
#                     required=False)
# parser.add_argument('-outPath',
#                     help='Path for the output files',
#                     dest="pathToSave",
#                     required=True)
# arguments = parser.parse_args()


#main(arguments.data, arguments.nvar, arguments.nvaruse, arguments.pathToSave)
data = getDataFromFile(sys.argv[0])
main(data, sys.argv[1], sys.argv[2], sys.argv[3])
#print(sys.argv)