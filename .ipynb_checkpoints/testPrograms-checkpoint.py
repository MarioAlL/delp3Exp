import subprocess
from utilsExp import *
def testProgram(pathToProgram, literal):
    with open(pathToProgram, 'r') as f:
        lines = f.readlines()
        # remove spaces
        lines = [line.replace(' ', '').rstrip() for line in lines]
        delpProgramString = ''.join(lines)
        cmd = ['./globalCore', 'stream', delpProgramString, 'answ', literal]
        proc = subprocess.Popen(cmd, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        o, e = proc.communicate()
        
        if(proc.returncode == 0):
            print(o.decode('ascii'))
        else:
            print_error_msj("Error to consult literal")
            exit()

testProgram('./programs/textLables.delp', 'a')
