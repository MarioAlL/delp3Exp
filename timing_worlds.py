import sys
import os.path
from utilsExp import getDataFromFile
import numpy as np

#BN_MODELS_PATH = '/home/mario/results/tool/DAQAPExp/30/alpha09/'
RESULTS_PATH07 = '/home/mario/results/tool/DAQAPExp/30/alpha07/bn/250000/'
RESULTS_PATH09 = '/home/mario/results/tool/DAQAPExp/30/alpha09/bn/250000/'
# all_literals = ['a','b','c','d','e','f','g','h','i','j']
# program_literals = ['0','1','2','3','4','5','6','7','8','9']


program_literals = [
    ['0',['f']],
    ['1',['b','e','g']],
    ['2',['f']],
    ['3',['a','c','d','h','i','j']],
    ['4',['a','b','d','f','g','h','j']],
    ['5',['g','j']],
    ['6',['j']],
    ['7',['b','d']],
    ['8',['b','e','f','h','i']]
]
# script_descriptor = open("sampleRandomSampling.py")
#
# a_script = script_descriptor.read()
# for program in program_literals:
#     literal = np.random.choice(all_literals)
#     sys.argv = [
#     literal, # Literal to consult
#     100, #samples
#     BN_MODELS_PATH + program + 'models.json', # Programa
#     program, #BN name,
#     BN_MODELS_PATH, #BN path
#     RESULTS_PATH + program, # Result path
#     'globalCore'
#     ]
#     exec(a_script)
# script_descriptor.close()

def get_aver_time_worlds():
    total = 0
    i = 0
    for program in program_literals:
        for literal in program[1]:
            if os.path.isfile(RESULTS_PATH07 + program[0] + literal + 'sampleRandomResults.json'):
                data = getDataFromFile(RESULTS_PATH07 + program[0] + literal + 'sampleRandomResults.json')
                total += data['worldsAnalyzed'] - data['repeatedWorlds']
                i += 1
    total = total / i
    print(total)

get_aver_time_worlds()
