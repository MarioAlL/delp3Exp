from utilsExp import *
import sys

def onlyDeLPRules(rules):
    pi = ''
    delta = ''
    factsAndSR = [rule for rule in rules if '<-' in rule]
    defeasibleRules = [rule for rule in rules if '-<' in rule]
    for rule in factsAndSR:
        aux = rule.split('<-')
        pi = pi + '\n' + '$\srule{' + aux[0].strip() + '}{' + aux[1].strip() + '}$'
    for rule in defeasibleRules:
        aux = rule.split('-<')
        delta = delta + '\n' + '$\drule{' + aux[0].strip() + '}{' + aux[1].strip() + '}$'

    toWrite = pi + '\n\n'+ delta
    print(toWrite)
    with open('latexProgram.txt', 'w') as program:
        program.write(toWrite)

def deLPRulesAndLabels(rules):
    pi = ''
    delta = ''
    for rule in rules:
        if('<-' in rule[0]):
            #Strict or Fact
            aux = rule[0].replace('~', '\sim ').split('<-')
            pi = pi + '\n' + '$\srule{' + aux[0].strip() + '}{' + aux[1].strip() + '}$ :  ' + rule[1]
        else:
            #Defeasible
            aux = rule[0].replace('~', '\sim ').split('-<')
            delta = delta + '\n' + '$\drule{' + aux[0].strip() + '}{' + aux[1].strip() + '}$ :  ' + rule[1]        
        
    
    toWrite = pi + '\n\n'+ delta
    print(toWrite)
    with open('latexProgramLables.txt', 'w') as program:
        program.write(toWrite)

filePath = sys.argv[1]
data = getDataFromFile(filePath)
#onlyDeLPRules(data['rules'])
deLPRulesAndLabels(data['af'])