import sys
import numpy as np

from utilsExp import getDataFromFile

# all_literals = ['a','b','c','d','e','f','g','h','i','j']
# program_literals = [
#     ['5', all_literals],
#     ['6', all_literals],
#     ['7', all_literals],
#     ['8', all_literals],
#     ['9', all_literals]
# ]
# 10 atoms
# program_literals = [
#     ['0',['e','i']],
#     ['1',['g']],
#     ['2',['f','h','i']],
#     ['3',['a','b','j']],
#     ['4',['d']],
#     ['5',['b','e','f','h']],
#     ['6',['j']],
#     ['7',['a','b','c','d','f','g','h','i','j']],
#     ['8',['a','d','e','h','i']],
#     ['9',['a','c','d','f','g']]
#     ]

#15 atoms
# program_literals = [
#     ['0',['g']],
#     ['1',['b','c','d','e','f','g','h','j']],
#     ['2',['c','g',]],
#     ['3',['a','b','d','j']],
#     ['4',['b','f','g','h','j']],
#     ['5',['b','d','f','g']],
#     ['6',['f']],
#     ['7',['b','e','f','h']],
#     ['8',['e','g','h','i']],
#     ['9',['g']]
# ]


# 20 atoms PRIMERA VERSION
# program_literals = [
#     ['0',['d','e','g','h','i']],
#     ['1',['a','c','e','f','h']],
#     ['4',['a','d']],
#     ['7',['a']]
# ]

#30 atoms
# program_literals = [
#     ['0',['f']],
#     ['1',['b','e','g']],
#     ['2',['f']],
#     ['3',['a','c','d','h','i','j']],
#     ['4',['a','b','d','f','g','h','j']],
#     ['5',['g','j']],
#     ['6',['j']],
#     ['7',['b','d']],
#     ['8',['b','e','f','h','i']]
# ]
program_literals = [
    ['7',['b','d']],
    ['8',['b','e','f','h','i']]
]

# def random_big_programs():
#     program_literals = []
#     programs = 10
#     literals = ['a','b','c','d','e','f','g','h','i','j']
#     for i in range(28):
#         program = np.random.choice(programs)
#         literal = np.random.choice(literals)
#         program_literals.append([program, literal])
#     print(program_literals)
#
# random_big_programs()

# def print_results():
#     to_write = ''
#     for program_literal in program_literals:
#         for literal in program_literal[1]:
#             result = getDataFromFile('/home/mario/results/tool/DAQAPExp/30/alpha09/bn/250000/' \
#             + program_literal[0] + literal + 'sampleRandomResults.json')
#             #to_write += program_literal[0] + ' | ' + literal + "\n" #PROGRAMS | LITERAL
#             to_write += "[" + "{:.4f}".format(result["l"]) + " - " + "{:.4f}".format(result["u"]) + "]" + '\n' #INTERVALO
#             #to_write += "{:.2f}".format(result["timeExecution"][0]) + "\n" # TIEMPO Sampling
#             #to_write += str(int(result["timeExecution"])) + "\n" # TIEMPO EXACTO
#     with open('/home/mario/results/tool/DAQAPExp/30/alpha09/resultBN.txt', 'w') as outfile:
#         outfile.write(to_write)
#
# print_results()

# def getMetric(aprox, exact):
#     # aprox = [l,u]
#     # exact = [l,u]
#     width_aprox = aprox[1] - aprox[0]
#     width_exact = exact[1] - exact[0]
#     remainder_aprox = 1 - width_aprox
#     remainder_exact = 1 - width_exact
#     metric = remainder_aprox / remainder_exact
#     return "{:.4f}".format(metric)
#
#
# def compute_metric():
#     path_aproximation = '/home/mario/results/tool/DAQAPExp/15/alpha07/bn/1000/'
#     path_exact = '/home/mario/results/tool/DAQAPExp/15/alpha07/'
#     to_write = ''
#     for program_literal in program_literals:
#         for literal in program_literal[1]:
#             aproximation = getDataFromFile(path_aproximation + program_literal[0] + literal + 'sampleRandomResults.json')
#             exact = getDataFromFile(path_exact + program_literal[0] + literal + 'INTERESTexactResults.json')
#             metric = getMetric([aproximation['l'], aproximation['u']], [exact['l'], exact['u']])
#             to_write += metric + '\n'
#     with open(path_exact + 'metric.txt', 'w') as outfile:
#         outfile.write(to_write)
#
# compute_metric()

script_descriptor = open("sampleRandomSampling.py")

a_script = script_descriptor.read()
for program_literal in program_literals:
    #n_program = str(program)
    for literal in program_literal[1]:
        sys.argv = [
        literal, # Literal to consult
        250000, #samples
        '/home/mario/results/tool/DAQAPExp/30/alpha07/' + program_literal[0] + 'models.json', # Programa
        program_literal[0], #BN name,
        '/home/mario/results/tool/DAQAPExp/30/alpha07/', #BN path
        '/home/mario/results/tool/DAQAPExp/30/alpha07/bn/250000/' + program_literal[0] + literal, # Result path
        'globalCore1'
        ]
        exec(a_script)
script_descriptor.close()
