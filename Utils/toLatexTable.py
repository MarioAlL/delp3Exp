import re
import sys
import json
from utilsExp import *


tableRowStructure= "& \multicolumn{1}{c|}{yTotal} & \multicolumn{1}{c|}{yPerc}   & \multicolumn{1}{c|}{nTotal}  & \multicolumn{1}{c|}{nPerc}   & \multicolumn{1}{c|}{undTotal}  & \multicolumn{1}{c|}{undPerc} & \multicolumn{1}{c|}{0} & \multicolumn{1}{c|}{0}  & \multicolumn{1}{c|}{$[pLow-pUpper]$}                           & \multicolumn{1}{c|}{tExec}"

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

def main(results):
    rows = ''
    for result in results:
        data = getDataFromFile(result)

        rep = {"yTotal": str(data["yes"]["total"]), "yPerc": str(data["yes"]["perc"]).replace('.',','), "nTotal": str(data["no"]["total"]), "nPerc": str(data["no"]["perc"]).replace('.',','), "undTotal": str(data["und"]["total"]), "undPerc": str(data["und"]["perc"]).replace('.',','), 'pLow':str(data["l"]).replace('.',','), 'pUpper':str(data["u"]).replace('.',','), 'tExec':str(data["execution_time"])} # define desired replacements here
        # use these three lines to do the replacement
        rep = dict((re.escape(k), v) for k, v in rep.items())
        #Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], tableRowStructure)
        rows += text + '\n\n\n'

    with open('forLatexTable.txt', 'w') as program:
        program.write(rows)

def mainSimpleRow(number_of_programs):
    literals_to_consult = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o"
    ]
    to_write = ''
    for program in range(number_of_programs):
        n_program = str(program)
        lit_probs = {}
        for literal in literals_to_consult:
            program_path = "/home/mario/results/tool/10/smallGiani/" + n_program + literal + "exactResults.json"
            data = getDataFromFile(program_path)
            lit_probs[literal] = "[" + str(data["l"]) + "-" + str(data["u"]) + "]"
        # row = n_program + " & " + str(lit_probs["l_0"]) + " & " + str(lit_probs["l_1"]) + " & " + str(lit_probs["l_2"]) + " & " \
        # + str(lit_probs["l_3"]) + " & " + str(lit_probs["l_4"]) + " & "\
        # + str(lit_probs["l_5"]) + " & " + str(lit_probs["l_6"]) + " &"\
        # + str(lit_probs["l_7"])+ " & " + str(lit_probs["l_8"]) + " & "\
        # + str(lit_probs["l_9"])

        row = n_program
        for key, value in lit_probs.items():
            row += ' & ' + str(value)


        to_write += row + '\\' + "\n"
    with open("forSimpleRowTable.txt", "w") as probabilities:
        probabilities.write(to_write)


#files = sys.argv[1:]
#main(files)
number_of_programs = sys.argv[1]

mainSimpleRow(int(number_of_programs))
