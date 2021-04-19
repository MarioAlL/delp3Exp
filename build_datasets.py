import argparse
from buildKBs import *
from utilsExp import *

class Experiment:
    
    # Some default configurations for models
    #
    # Analytical Model
    am_settings = {
            'simple': 'S',  # Dataset path of simples delp programs
            'medium' : 'M', # Dataset path of mediums delp programs
            'complex': 'C' # Dataset path of complex delp programs
            }
    # Annotation Function
    af_settings = {
            'simple':{
                'fa_ann': 0,    # Only kb base is annotated
                'var_use': 1,
                'operators': 0  # No operators
                },
            'medium':{
                'fa_ann': 50,
                'var_use': 2,
                'operators': 1  # And or OR
                },
            'complex':{
                'fa_ann': 100,
                'var_use': 3,
                'operators': 2  # And and OR
                }
            }
    # Environmental Model
    em_settings = {
            'simple': {
                'var': 10,
                'var_use_annot': 10,
                'arcs': 0,  # To use Tup-Ind
                'alpha': 0,
                'tau': 0
                },
            'medium':{
                'var': 20,
                'var_use_annot': 20,
                'arcs': 20,  
                'alpha': 0.9,
                'tau': 1    # Similar to tree structure
                },
            'complex':{
                'var': 25,
                'var_use_annot': 25,
                'arcs': 30,  
                'alpha': 0.6,
                'tau': 2
                } 
            }
    

    def __init__(self, result_path) -> None:
        # The object for create the datasets
        self.model_creator = CreateDeLP3E()
        self.result_path = result_path
    

    def build_models(self, am, am_setting: str, af_setting: str, em_setting: str) -> None:
        """ To create setting for the experiment
        Args:
            -am_setting: 'simple', 'medium' or 'complex'
            -af_setting: 'simple', 'medium' or 'complex'
            -em_setting: 'simple', 'medium' or 'complex'
        """
        self.model_creator.main(am, self.em_settings['simple']['var'], self.em_settings['simple']['var_use_annot'], False, self.result_path)


parser = argparse.ArgumentParser(description='Script to generate annotations \
                                                randomly for a del3e program')
parser.add_argument('-am',
                    action='store',
                    help="The path of the dataset with delp programs (in json format)",
                    dest="am",
                    type=get_all_delp,
                    required=True)
#parser.add_argument('-vem',
#                    help='Number of environmental variables',
#                    dest="var_em",
#                    type=int,
#                    required=True)
#parser.add_argument('-vu',
#                    help='Number of environmental variables to use in annotations',
#                    dest="var_used",
#                    type=int,
#                    required=True)
#parser.add_argument('-vannot',
#                    help='Environmental variables to use in each annotation',
#                    dest='var_annot',
#                    type=bool,
#                    required=False)
#parser.add_argument('-use_op',
#                    help='Operator to use (1 = AND or OR, 2 = AND and OR)',
#                    dest="operators",
#                    required=False)
parser.add_argument('-out',
                    help='Path for the output file',
                    dest="output_path",
                    required=True)
#
## To call from another python file
##arguments = parser.parse_args(sys.argv)
arguments = parser.parse_args()
#
###### To call from other script #####
## sys.argv = [
## '-delppath', 'DeLP Program path',
## '-nvar', 'Int',
## '-nvaruse', 'Int',
## '-outpath', 'Result path'
## ]
#main(arguments.delp, arguments.var_em,
#    arguments.var_used, arguments.var_annot, arguments.output_path)
test = Experiment(arguments.output_path)
test.build_models(arguments.am, 'simple', 'simple', 'simple')


