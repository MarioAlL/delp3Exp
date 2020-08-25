from progress.spinner import Spinner
from progress.bar import IncrementalBar
from consultDeLP import *
import time
import argparse
from em.bn import *
import sys

uniquePrograms, uniquesWorlds = set(), set()
bayesianNetwork, allWorlds, globalProgram, predicates = '', '', '', ''
results = {
    'literal': '',
    'yes':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'no':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'und':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'unk':{
        'total':0,
        'perc':0.00,
        'prob':0.00
    },
    'l':0.00,
    'u':1.00,
    'timeExecution': [],
    'worldsAnalyzed': 0,
    'repeatedWorlds': 0,
    'program': '',
    'atomos': '',
    'atomUsed': ''
}


def startSampling(literal, pathResult):
    global uniquesWorlds, uniquePrograms
    numberOfWorlds = allWorlds
    dim = len(predicates)
    numberOfAllWorlds = pow(2, dim)
    print_ok_ops('Starting random sampling...')
    bar = IncrementalBar('Processing worlds', max=numberOfWorlds)
    initialTime = time.time()
    for i in range(numberOfWorlds):
        #worldData = allWorlds[i]
        randomNum = np.random.choice(numberOfAllWorlds,1)
        worldData = int_to_bin_with_format(randomNum[0], dim)
        worldAsTuple = tuple(worldData[0])
        if(not worldAsTuple in uniquesWorlds):
            uniquesWorlds.add(worldAsTuple)
            world = worldData[0]
            evidence = worldData[1]
            prWorld = bayesianNetwork.get_sampling_prob(evidence)
            # Build the PreDeLP Program for a world
            delpProgram = map_world_to_program(globalProgram, predicates, world)
            status = queryToProgram(delpProgram, literal, uniquePrograms)
            if status[1] == 'yes':
                results['yes']['total'] += 1
                results['yes']['prob'] = results['yes']['prob'] + prWorld
            elif status[1] == 'no':
                results['no']['total'] += 1
                results['no']['prob'] = results['no']['prob'] + prWorld
            elif status[1] == 'undecided':
                results['und']['total'] += 1
                results['und']['prob'] = results['und']['prob'] + prWorld
            elif status[1] == 'unknown':
                results['unk']['total'] += 1
                results['unk']['prob'] = results['unk']['prob'] + prWorld
        bar.next()
    bar.finish()
    results['timeExecution'].append(time.time() - initialTime)
    results['worldsAnalyzed'] = numberOfWorlds
    results['repeatedWorlds'] = results['worldsAnalyzed'] - len(uniquesWorlds)
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']
    results['literal'] = literal
    results['program'] = globalProgram
    results['atomos'] = predicates
    results['atomUsed'] = predUsed

    #Save file with results
    with open(pathResult + 'sampleRandomResults.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)

   #Save the unique worlds
    #save_unique_worlds(uniquesWorlds, 'random', pathResult)

    # Print the results
    print_ok_ops("Results: ")
    print("Unique worlds: ", end='')
    print_ok_ops("%s" % (len(uniquesWorlds)))
    print("Unique programs: ", end='')
    print_ok_ops("%s" % (len(uniquePrograms)))
    print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))

def start_dist_sampling(literal, pathResult, coreName):
    global uniquesWorlds, uniquePrograms
    # numberOfWorlds = allWorlds
    # dim = len(predicates)
    # numberOfAllWorlds = pow(2, dim)

    print_ok_ops('Starting random sampling from BN...')
    #bar = IncrementalBar('Processing worlds', max=allWorlds)
    spinner = Spinner("Processing")
    initialTime = time.time()
    worlds = bayesianNetwork.gen_samples(allWorlds)
    for worldData in worlds:
        #worldData = allWorlds[i]
        # randomNum = np.random.choice(numberOfAllWorlds,1)
        # worldData = int_to_bin_with_format(randomNum[0], dim)
        worldAsTuple = tuple(worldData[0])
        if(not worldAsTuple in uniquesWorlds):
            uniquesWorlds.add(worldAsTuple)
            world = worldData[0]
            evidence = worldData[1]
            prWorld = bayesianNetwork.get_sampling_prob(evidence)
            # Build the PreDeLP Program for a world
            delpProgram = map_world_to_program(globalProgram, predicates, world)
            status = queryToProgram(delpProgram, literal, uniquePrograms, coreName)
            if status[1] == 'yes':
                results['yes']['total'] += 1
                results['yes']['prob'] = results['yes']['prob'] + prWorld
            elif status[1] == 'no':
                results['no']['total'] += 1
                results['no']['prob'] = results['no']['prob'] + prWorld
            elif status[1] == 'undecided':
                results['und']['total'] += 1
                results['und']['prob'] = results['und']['prob'] + prWorld
            elif status[1] == 'unknown':
                results['unk']['total'] += 1
                results['unk']['prob'] = results['unk']['prob'] + prWorld
            spinner.next()
    #     bar.next()
    # bar.finish()
    results['timeExecution'].append(time.time() - initialTime)
    results['worldsAnalyzed'] = allWorlds
    results['repeatedWorlds'] = results['worldsAnalyzed'] - len(uniquesWorlds)
    results['yes']['perc'] = "{:.2f}".format((results['yes']['total'] * 100) / results['worldsAnalyzed'])
    results['no']['perc'] = "{:.2f}".format((results['no']['total'] * 100) / results['worldsAnalyzed'])
    results['und']['perc'] = "{:.2f}".format((results['und']['total'] * 100) / results['worldsAnalyzed'])
    results['unk']['perc'] = "{:.2f}".format((results['unk']['total'] * 100) / results['worldsAnalyzed'])
    results['l'] = results['yes']['prob']
    results['u'] = results['u'] - results['no']['prob']
    results['literal'] = literal
    results['program'] = globalProgram
    results['atomos'] = predicates
    results['atomUsed'] = predUsed

    #Save file with results
    with open(pathResult + 'sampleRandomResults.json', 'w') as outfile:
        json.dump(results, outfile, indent=4)

   #Save the unique worlds
    #save_unique_worlds(uniquesWorlds, 'random', pathResult)

    # Print the results
    # print_ok_ops("Results: ")
    # print("Unique worlds: ", end='')
    # print_ok_ops("%s" % (len(uniquesWorlds)))
    # print("Unique programs: ", end='')
    # print_ok_ops("%s" % (len(uniquePrograms)))
    # print_ok_ops("Prob(%s) = [%.4f, %.4f]" % (literal, results['l'], results['u']))


def main(literal, samples, models, bn, pathResult, coreName):
    global allWorlds, globalProgram, predicates, bayesianNetwork, predUsed

    bayesianNetwork = bn
    allWorlds = samples
    #allWorlds = genSamples(bn, samples, pathResult)
    globalProgram = models["af"]
    predicates = models["randomVar"]
    predUsed = len(models["varUsed"])

    #startSampling(literal, pathResult)
    start_dist_sampling(literal, pathResult, coreName)

# parser = argparse.ArgumentParser(
#     description="Script to perform the Sampling experiment (Random)")
#
# parser.add_argument('-l',
#                     help='The literal to calculate the probability interval',
#                     action='store',
#                     dest='literal',
#                     required=True)
# # parser.add_argument('-p',
# #                     help='The DeLP3E program path',
# #                     action='store',
# #                     dest='program',
# #                     type=getDataFromFile,
# #                     required=True)
# # parser.add_argument('-bn',
# #                     help='The Bayesian Network file path (only "bifxml" for now)',
# #                     action='store',
# #                     dest='bn',
# #                     type=loadBN,
# #                     required=True)
# # parser.add_argument('-pathR',
# #                     help='Path to save the results (with file name)',
# #                     dest='pathResult',
# #                     required=True)
# parser.add_argument('-s',
#                     help='Number of samples (in random setting)',
#                     dest='samples',
#                     type=int,
#                     required=True)
# arguments = parser.parse_args()

# pathToProgram = "/home/mario/results/tool/prueba/4models.json"
# pathResult = "/home/mario/results/tool/prueba/"
# program = getDataFromFile(pathToProgram)
# myBN = BayesNetwork('4TEST', '/home/mario/results/tool/prueba/')

literal = sys.argv[0]
samples = sys.argv[1]
pathToProgram = sys.argv[2]
program = getDataFromFile(pathToProgram)
myBN = BayesNetwork(sys.argv[3] + 'TEST', sys.argv[4])
myBN.load_bn()
pathToResult = sys.argv[5]
coreName = sys.argv[6]
main(literal, samples, program, myBN, pathToResult, coreName)
