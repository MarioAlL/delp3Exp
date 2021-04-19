import sys

from utilsExp import getDataFromFile

all_literals = ['a','b','c','d','e','f','g','h','i','j']
program_literals = [
    ['5', all_literals],
    ['6', all_literals],
    ['7', all_literals],
    ['8', all_literals],
    ['9', all_literals]
]
# number_of_programs = 10
# script_descriptor = open("buildD3EProgram.py")
# a_script = script_descriptor.read()
# for program in range(number_of_programs):
#  #sys.argv = ['/home/mario/results/tool/alternative/small/delp' + str(program) + '.delp', 10, 10, '/home/mario/results/tool/10/smallAlter/' + str(program)]
#  sys.argv = ['/home/mario/results/tool/genGiani/small/delp' + str(program) + '.delp', 30, 30, '/home/mario/results/tool/30/' + str(program)]
#  exec(a_script)
# script_descriptor.close()

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
#     ['4',['a','d','f']],
#     ['7',['a']]
# ]
# program_literals = [
#     ['1',['e','f','h']],
#     ['4',['a','d','f']],
#     ['7',['a']]
# ]

#number_of_programs = [1,2,3,4,5,6,7,8,9]
script_descriptor = open("exactSampling.py")
a_script = script_descriptor.read()
#literals_to_consult = [literal for literal in getDataFromFile('/home/mario/results/tool/genGiani/small/delp0.delp')["literals"] if ('~' not in literal)] # GIANI
#literals_to_consult = [literal for literal in getDataFromFile('/home/mario/results/tool/alternative/small/delp0.delp')["literals"] if ('~' not in literal)] # Alter
#literals_to_consult = ["l_5","l_6","l_7","l_8","l_9"]
#print(literals_to_consult)
#for program in range(number_of_programs):
for program in program_literals:
    n_program = program[0]
    for literal in program[1]:
        path = '/home/mario/results/tool/DAQAPExp/15/todos/alpha07/' + n_program + literal + 'INTERESTexactResults.json'
        if not os.path.isfile(path):
            sys.argv = ['/home/mario/results/tool/DAQAPExp/15/todos/alpha07/' + n_program + 'models.json', # DeLP3E program
                        '/home/mario/results/tool/DAQAPExp/15/todos/alpha07/' + n_program + literal, # Path to save result
                        n_program, # BN name
                        '/home/mario/results/tool/DAQAPExp/10/todos/alpha07/', # BN path
                        literal,
                        'globalCore1']
            exec(a_script)
script_descriptor.close()
