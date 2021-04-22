import sys
sys.path.insert(1, './Utils/')
sys.path.insert(2, './EM/BNs/')
from utilsExp import *
import argparse
import numpy as np
from bn import *
import pyAgrum as gum


class CreateDeLP3E: 
    neg_probs = [0.80, 0.20] # [Prob for literal, Prob for negated literal]

    def __init__(self, am: list, fa_ann: int, 
                        var_use_ann: int, em_var: int,
                        em_var_use_ann: int, operators: int,
                        arcs: int, alpha: int, tau: int, 
                        path_to_save: str) -> None:
        self.delp_programs = am
        self.fa_ann = fa_ann 
        self.var_use_ann = var_use_ann
        self.em_var = em_var
        self.em_var_use_ann = em_var_use_ann
        self.operators = operators
        self.arcs = arcs
        self.alpha= alpha
        self.tau = tau
        self.path_to_save = path_to_save
        self.utils = Utils()


    def assign_labels_formulas(self, rules, to_all_rules):
        #to_all is for assign the labels only to defeasible rules or all rules
        af = []
        if to_all_rules:
            for rule in rules:
                label = np.random.random(1)[0]  # The label
                formula = self.get_simple_formula()
                af.append(
                    ['('+ rule +')::' + str(label)[:4] + ';', formula])
        else:
            for rule in rules:
                if '-<' in rule:
                    label = np.random.random(1)[0]
                else:
                    label = 1.00
                formula = self.get_simple_formula()
                af.append(
                    ['('+ rule +')::' + str(label)[:4] + ';', formula])
        return af
    

    def filter_rules(self, rules: list) -> list:
        filtered_rules = []

        if self.fa_ann == 0:
            # Only the facts and presumptions are annotated
            filtered_rules = [rule for rule in rules if '<- true' in rule or 
                                                        '-< true' in rule]
        elif self.fa_ann < 100:
            perc = int((self.fa_ann * len(rules)) / 100)
            filtered_rules = np.random.choice(rules, perc)
        else:
            # All delp program is annotated
            filtered_rules = rules

        return filtered_rules


    def get_annotation(self) -> str:
        return "Annotation test"



    def build_BN(self,nodes, arcs, alpha_entropy, path_to_save):
        #For build a random Bayesian Network
        bayesian_network = BayesNetwork('BN',path_to_save)
        bayesian_network.build_save_random_BN(nodes, arcs, True)
        if alpha_entropy != 0:
            # To change the entropy
            bayesian_network.make_CPTs(bayesian_network.structure[0], alpha_entropy)


    def create(self) -> None: 
        for path_delp_program in self.delp_programs:
            delp_program = self.utils.getDataFromFile(path_delp_program)
            delp_rules = [rule[:-1] for rule in delp_program['delp']]
            rule_to_annot = self.filter_rules(delp_rules)
            af = []
            for rule in delp_rules:
                if rule in rule_to_annot:
                    annotation = self.get_annotation()
                    af.append([rule + ';', annotation])
                else:
                    af.append([rule + ';', ""])
            
            # Create the Environmental Model
            # ...

            # To save the delp3e model
            delp3e_model = {
                    "em_var": self.em_var,
                    "em_var_use_ann": self.em_var_use_ann,
                    "literals": delp_program['literals'],
                    "af": af
                    }
            
            # Save the delp3e file
            self.utils.write_json(delp3e_model, self.path_to_save + 'AAKJSDA')



        

        #if(nvaruse <= nvar):
        #    # Generate variables
        #    randomVar = [str(var) for var in list(range(nvar))]
        #    # Get all rules from the delp program
        #    rules = [rule[:-1] for rule in data["delp"]]
        #    # Get the first nvaruse from randomVar
        #    randomVarToUse = randomVar[:nvaruse]
        #    randomVarToUse.append('True')
        #    # Assign probabilities to each variables to use
        #    probs = []
        #    self.var_to_use_probs["variables"] = randomVarToUse
        #    self.var_to_use_probs["probs"] = probs
        #    if with_labels:
        #        af = self.assign_labels_formulas(rules, False)
        #    else:
        #        af = self.assign_formulas(rules)

        #    program = {
        #        "random_var": randomVar,
        #        "var_used": randomVarToUse,
        #        "af": af
        #    }

        #    write_json_file(program, path_to_save + 'KB')   # Save the KB

        #    nodes = nvar #  Number of nodes for the Bayesian Network
        #    arcs = nvar #   Max number of arcs for the Bayesian Network
        #    alpha_entropy = 0 # 0 Max entropy, 1 Min entropy
        #    self.build_BN(nodes, arcs, alpha_entropy, path_to_save)
        #    print("KB generated")
        #else:
        #    print_error("Error: nvaruse > nvar")
        #    exit()


    def get_simple_formula(self):
        # To build simple formulas with one atom
        if len(self.var_to_use_probs["probs"]) != 0:
            variable = np.random.choice(self.var_to_use_probs["variables"],
                                        1,
                                        p = self.var_to_use_probs["probs"],
                                        replace = True)
        else:
            variable = np.random.choice(self.var_to_use_probs["variables"],
                                        1,
                                        replace = True)
        negation = np.random.choice(["","not "], 1, p = self.neg_probs, replace = True)
        formula = str(negation[0]) +str(variable[0])
        return formula

    def get_formula(self):
        # To build formulas with two atoms and one operator
        if(len(probs) > 0):
            atoms = np.random.choice(variables, 2, p= probs, replace=True)
        else:
            atoms = np.random.choice(variables, 2, replace=True)

        if 'True' in atoms:
            return 'True'
        else:
            operator = np.random.choice(['and','or'], 1, replace=True)
            return str(atoms[0] + ' ' + operator[0] + ' ' + atoms[1])
