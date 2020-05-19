import re
import sys
import json


tableRowStructure= "& \multicolumn{1}{c|}{yTotal} & \multicolumn{1}{c|}{yPerc}   & \multicolumn{1}{c|}{nTotal}  & \multicolumn{1}{c|}{nPerc}   & \multicolumn{1}{c|}{undTotal}  & \multicolumn{1}{c|}{undPerc}   & \multicolumn{1}{c|}{$[pLow-pUpper]$}                           & \multicolumn{1}{c|}{1450}"

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

        rep = {"yTotal": str(data["yes"]["total"]), "yPerc": str(data["yes"]["perc"]).replace('.',','), "nTotal": str(data["no"]["total"]), "nPerc": str(data["no"]["perc"]).replace('.',','), "undTotal": str(data["und"]["total"]), "undPerc": str(data["und"]["perc"]).replace('.',','), 'pLow':str(data["l"]).replace('.',','), 'pUpper':str(data["u"]).replace('.',',')} # define desired replacements here
        # use these three lines to do the replacement
        rep = dict((re.escape(k), v) for k, v in rep.items()) 
        #Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], tableRowStructure)
        rows += text + '\n\n\n'

    with open('forLatexTable.txt', 'w') as program:
        program.write(rows)

files = sys.argv[1:]
main(files)