import sys
import numpy as np
import os.path
from utilsExp import getDataFromFile

# all_literals = ['a','b','c','d','e','f','g','h','i','j']
# program_literals = [
#     ['0', all_literals],
#     ['1', all_literals],
#     ['2', all_literals],
#     ['3', all_literals],
#     ['4', all_literals],
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


#20 atomos alpha 0.9 Total
# program_literals = [
#     ['0',['a','b','c','d','e','f','g','h','i']],
#     ['1',['a','b','c','d','e','f','g','h','i','j']],
#     ['2',['a','b']],
#     ['4',['a','b','c','d','e','f','g']],
#     ['7',['a']]
# ]
#20 atomos alpha 0.7 Total (Gerardo)
program_literals = [
    ['0',['d','e','g','h','i']],
    ['1',['a','b','c','d','e','f','g','h']],
    ['5',['b','d','e','f','g','h']],
    ['6',['b','c','e','f','j']]
]

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
# program_literals = [
#     ['4',['b','d']]
# ]

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

def getMetric(aprox, exact):
    # aprox = [l,u]
    # exact = [l,u]
    width_aprox = aprox[1] - aprox[0]
    width_exact = exact[1] - exact[0]
    remainder_aprox = 1 - width_aprox
    remainder_exact = 1 - width_exact
    if remainder_exact == 0:
        metric = 0
    else:
        metric = remainder_aprox / remainder_exact
    return "{:.4f}".format(metric)

def is_bad_program(interval):
    width = interval[1] - interval[0]
    remaind = 1 - width
    if remaind == 0:
        return True
    else:
        return False


def print_results():
    interest = 0
    to_write = ''
    for program_literal in program_literals:
        for literal in program_literal[1]:
            path_aprox = '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/bn/10000/' \
            + program_literal[0] + literal + 'sampleRandomResults.json'

            path_exact = '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/' \
            + program_literal[0] + literal + 'exactResults.json'
            # path_exact = '/home/mario/Dropbox/DocDROP/Mario Leiva/Sampling/version windows/results07/' \
            # + program_literal[0] + literal + 'exactResults.json'

            if os.path.isfile(path_exact):
                # path_exact = path_exact = '/home/mario/results/tool/DAQAPExp/20/todos/alpha09/' \
                # + program_literal[0] + literal + 'INTERESTexactResults.json'
                result_exact = getDataFromFile(path_exact)
                if not is_bad_program([result_exact['l'], result_exact['u']]):
                    result_aprox = getDataFromFile(path_aprox)
                    #to_write += "[" + "{:.4f}".format(result_exact["l"]) + " - " + "{:.4f}".format(result_exact["u"]) + "]" + '\n' #INTERVALO EXACTO
                    #to_write += "[" + "{:.4f}".format(result_aprox["l"]) + " - " + "{:.4f}".format(result_aprox["u"]) + "]" + '\n' #INTERVALO SAMPLING

                    #metric = getMetric([result_aprox['l'], result_aprox['u']], [result_exact['l'], result_exact['u']])
                    #to_write += metric + '\n'

                    #to_write += program_literal[0] + ' | ' + literal + "\n" #PROGRAMS | LITERAL
                    to_write += "{:.2f}".format(result_aprox["timeExecution"][0]) + "\n" # TIEMPO Sampling
                    #to_write += str(int(result_exact["timeExecution"])) + "\n" # TIEMPO EXACTO
                    interest += 1

    with open('/home/mario/results/tool/DAQAPExp/20/todos/alpha07/resultBN.txt', 'w') as outfile:
        outfile.write(to_write)
    print(interest)
print_results()




# def compute_metric():
#     path_aproximation = '/home/mario/results/tool/DAQAPExp/15/todos/alpha09/bn/100/'
#     path_exact = '/home/mario/results/tool/DAQAPExp/15/todos/alpha09/'
#
#
#     to_write = ''
#     for program_literal in program_literals:
#         for literal in program_literal[1]:
#             exact_path = path_exact + program_literal[0] + literal + 'INTERESTexactResults.json'
#             if not os.path.isfile(exact_path):
#                 exact_path = path_exact + program_literal[0] + literal + 'exactResults.json'
#             aproximation = getDataFromFile(path_aproximation + program_literal[0] + literal + 'sampleRandomResults.json')
#             exact = getDataFromFile(exact_path)
#             metric = getMetric([aproximation['l'], aproximation['u']], [exact['l'], exact['u']])
#             to_write += metric + '\n'
#     with open(path_exact + 'metric.txt', 'w') as outfile:
#         outfile.write(to_write)
#compute_metric()


# script_descriptor = open("sampleRandomSampling.py")
#
# a_script = script_descriptor.read()
# for program_literal in program_literals:
#     #n_program = str(program)
#     for literal in program_literal[1]:
#         sys.argv = [
#         literal, # Literal to consult
#         10000, #samples
#         '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/' + program_literal[0] + 'models.json', # Programa
#         program_literal[0], #BN name,
#         '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/', #BN path
#         '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/bn/10000/' + program_literal[0] + literal, # Result path
#         'globalCore'
#         ]
#         exec(a_script)
# script_descriptor.close()
