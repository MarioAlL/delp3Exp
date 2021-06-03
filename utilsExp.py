from termcolor import cprint
import json
import os
import glob
import copy
import re

""" General Utils"""
def print_info(x): return cprint(x, 'grey', 'on_white')


def print_error(x): return cprint(x, 'red')


def print_ok(x): return cprint(x, 'green')


def compute_metric(aprox:list, exact:list):
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


def read_json_file(pathFile):
        try:
            file = open(pathFile, "r")
            toDict = json.load(file)
            file.close()
            return toDict
        except IOError:
            # print(e)
            print_error_msj("Error trying to open the file: %s" % (pathFile))
            exit()
        except ValueError:
            # print(e)
            print_error_msj("JSON incorrect format: %s" % (pathFile))
            exit()


def get_all_delp(dataset_path):
        if not os.path.isdir(dataset_path):
            self.print_error("The specified path does not exist")
            exit()
        else:
            delp_programs = glob.glob(dataset_path + 'delp*.json')
            if len(delp_programs) != 0:
                return delp_programs
            else:
                self.print_error("The specified path is empty")
                exit()

def get_perc(number, total):
    return "{:.2f}".format((number * 100) / total)

def write_results(results: json, path: str):
    worlds = results["data"]["n_worlds"]
    for lit, status in results["status"].items():
        status["percY"] = get_perc(status["yes"], worlds)
        status["percN"] = get_perc(status["no"], worlds)
        status["percU"] = get_perc(status["undecided"], worlds)
        status["percUNK"] = get_perc(status["unknown"], worlds)
        status["l"] = status["pyes"]
        status["u"] = 1 - status["pno"]
        if status["u"] - status["l"] <= 0.5:
            status["flag"] = "INTEREST"
    
    with open(path + "output.json", 'w') as outfile:
        json.dump(results, outfile, indent = 4)
""""""


class WorldProgramUtils:
    def __init__(self, am_dim: int, em_dim: int):
        self.to_format_program = '{0:0' + str(am_dim) + 'b}' 
        self.to_format_world = '{0:0' + str(em_dim) + 'b}'
        # Dictionary to save the delp programs and literals status
        self.delp_programs = {}
        pass

    
    def known_program(self, id_program: int):
        try:
            return self.delp_programs[id_program]
        except KeyError:
            return -1
   

    def unique_programs(self) -> int:
        return len(self.delp_programs.keys())
    
    def map_world_to_delp(self, model: list, world: list):
        delp = ''
        delp_bin = '0b'
        for rule, form in model:
            check_form = self.check_form(form, world)
            if check_form:
                delp = delp + rule
                delp_bin += '1'
            else:
                delp_bin += '0'
        id_program = int(delp_bin, 2)
        return [delp, id_program]

    
    def save_program_status(self, id_program: int, status: json):
        self.delp_programs[id_program] = status

    
    def id_program_to_format(self, id_program):
        program = [int(digit) for digit in list(self.to_format_program.format(id_program))]
        return program
   

    def id_world_to_format(self, id_world):
        world = [int(digit) for digit in list(self.to_format_world.format(id_world))]
        evidence = {i: world[i] for i in range(len(world))}
        return [world, evidence]
    
    
    def format_form(self, form, world): 
        to_eval = ''
        var_status = ''
        aux = form.strip().split(' ')
        for element in aux:
            try: 
                if world[int(element)] == 1:
                    var_status = "True"
                else:
                    var_status = "False"
            except ValueError:
                var_status = element 
            
            to_eval = to_eval + " " + var_status 

        return to_eval


    def check_form(self, form: str, world: list):
        if form == "" or form == "True":
            return True
        else:
            return eval(self.format_form(form, world))


    def is_evidence_ok(self, evidence, key, value):
        try:
            if evidence[key] == value:
                return True
            else:
                return False
        except KeyError:
            return True


    def get_program_evidence(self, rule_annot_status):
        delp_program = ''
        evidence = {}
        for rule, annot, status in rule_annot_status:
            if annot == "True" or annot == "":
                delp_program += rule
            elif annot == "not True":
                pass
            else:
                em_var = re.search(r'\d+', annot).group() 
                if status:
                    # The annotation must be True
                    if 'not' in annot:
                        # The em_var must be False
                        if self.is_evidence_ok(evidence, em_var, 0):
                            evidence[em_var] = 0
                            delp_program += rule
                        else:
                            # Inconsisten Program
                            return [-1,-1]
                            break
                    else:
                        # The em_var must be True
                        if self.is_evidence_ok(evidence, em_var, 1):
                            evidence[em_var] = 1
                            delp_program += rule
                        else:
                            # Inconsisten Program
                            return [-1,-1]
                            break
                else:
                    # The annotation must be False
                    if 'not' in annot:
                        # The em_var must be True
                        if self.is_evidence_ok(evidence, em_var, 1):
                            evidence[em_var] = 1
                        else:
                            # Inconsisten Program
                            return [-1,-1]
                            break
                    else:
                        # The em_var must be False 
                        if self.is_evidence_ok(evidence, em_var, 0):
                            evidence[em_var] = 0
                        else:
                            # Inconsisten Program
                            return [-1,-1]
                            break
        return [delp_program, evidence]            

