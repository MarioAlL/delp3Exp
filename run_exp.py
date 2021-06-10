import sys
import csv
import re
from utilsExp import *
from exactSampling import *
from byWorldSampling import *
from byProgramSampling import *
import argparse
from multiprocessing import Process

class Experiment:
    def __init__(self):
        pass

    
    def exact_sampling(self, models, models_path, output, approach):
        """
        :params
            -models: list
            -models_path: list
            -output: list
            -approach: str = ['worlds', 'programs']
        """
        if approach == 'worlds':
            # By worlds
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact = Exact(model, models_path, 'BNdelp' + index, output)
                exact.start_world_exact_sampling()
        else:
            # By programs
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact = Exact(model, models_path, 'BNdelp' + index, output)
                exact.start_program_exact_sampling()
    
    
    def by_world_sampling(self, models, models_path, output, samples, source):
        """
        :params
            -models: list
            -models_path: list
            -output: list
            -samples: int
            -source: str = ['dist', 'random']
        """
        if source == 'info':
            # Sampling from probability distribution
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact_values = read_json_file(gfnexact(model))
                interest_lit = exact_values["status"].keys()
                world_sampling = WorldSampling(model, models_path, gbn(index), 
                                                        output, interest_lit)
                world_sampling.start_distribution_sampling(samples)
        else:
            # Random sampling
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact_values = read_json_file(gfnexact(model))
                interest_lit = exact_values["status"].keys()
                world_sampling = WorldSampling(model, models_path, gbn(index), 
                                                        output, interest_lit)
                world_sampling.start_random_sampling(samples)


    def by_delp_sampling(self, models, models_path, output, samples, source):
        """
        :params
            -models: list
            -models_path: list
            -output: list
            -samples: int
            -amfilter: bool 
        """
        if source == 'info':
            # Filtering delp with em variables used
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact_values = read_json_file(gfnexact(model))
                interest_lit = exact_values["status"].keys()
                delp_sampling = ProgramSampling(model, models_path, gbn(index), 
                                                        output, interest_lit)
                delp_sampling.start_prefilter_sampling(samples)
        else:
            # Random delp sample from all possible combinations of rules
            for model in models:
                index = re.search(r'\d+', gfn(model)).group()
                exact_values = read_json_file(gfnexact(model))
                interest_lit = exact_values["status"].keys()
                delp_sampling = ProgramSampling(model, models_path, gbn(index), 
                                                        output, interest_lit)
                delp_sampling.start_random_sampling(samples)


    def analyze_results(self, files_path):
        """
        :params
            -files_path: str
        """
        results = glob.glob(files_path + 'modeldelp*output.json')
        total_time = 0.0
        interest = 0
        for result in results:    
            data = read_json_file(result)
            total_time += data["data"]["time"]
            for key, val in data["status"].items():
                if "flag" in val:
                    interest += 1
        print_ok("Total time: " + str(total_time))
        print_ok("Average: " + str(total_time / len(results)))
        print_ok("Interest: " + str(interest))


    def write_exact_csv(self, results_path):
        """
        :params
            -results_path: str
        """
        results = glob.glob(results_path + 'modeldelp*output.json')
        fieldnames = ['Prog','Lit', 'Exact', 'Time']
        rows =[]
        for result in results:
            n_program = re.search(r'\d+', gfn(result)).group()
            data = read_json_file(result)
            for lit, status in data["status"].items():
                if "flag" in status:
                    interval = '['+gf4(status["l"])+'-'+gf4(status["u"])+']'
                    rows.append(
                        {
                            'Prog': int(n_program),
                            'Lit': lit,
                            'Exact': interval,
                            'Time': format(status["time"],'.2f')
                        }
                    )
        ordered_rows = sorted(rows, key=lambda k: k['Prog'])
        with open(results_path + 'csvE_Results.csv', 'w', encoding='utf-8',
                                                            newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ordered_rows)


    def write_sampling_csv(self, results_path: str) -> None:
        results = glob.glob(results_path + 'modeldelp*output.json')
        fieldnames = ['Prog','Lit', 'Intervalo', 'Metric', 'Time', 'Mass']
        rows = []
        for result in results:
            program_name = gfn(result)
            n_program = re.search(r'\d+', program_name).group()
            data_sampling = read_json_file(result)
            exact = read_json_file(gfnexactSam(result) + program_name)
            for lit, lit_e in exact["status"].items():
                if "flag" in lit_e:
                    lit_s = data_sampling["status"][lit]
                    intervalo = '['+gf4(lit_s["l"])+'-'+gf4(lit_s["u"])+']'
                    metric = compute_metric([lit_s["l"], lit_s["u"]],
                                            [lit_e["l"], lit_e["u"]])
                    mass =  (lit_s["pyes"] + lit_s["pno"] + 
                            lit_s["pundecided"] + lit_s["punknown"])
                    rows.append(
                            {
                                'Prog': int(n_program),
                                'Lit': lit,
                                'Intervalo': intervalo,
                                'Metric': metric,
                                'Time': format(lit_s["time"], '.2f'),
                                'Mass': format(mass, '.4f')
                            }    
                        )       
        ordered_rows = sorted(rows, key=lambda k: k['Prog'])
        with open(results_path + 'csvS_Results.csv', 'w', encoding='utf-8', 
                                                            newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ordered_rows)


def run_parallel(models, obj_exp, func, params):
    # Params is a tuple
    mid = int(len(models)/2)
    total_models = len(models)
    models_1 = models[:mid]
    models_2 = models[mid:]
    init_time = time.time()
    p1 = Process(target=getattr(obj_exp,str(func)), args=(models_1,) + params)
    p2 = Process(target=getattr(obj_exp,str(func)), args=(models_2,) + params)
    print_info("Starting in parallel...")
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    end_time = time.time() - init_time
    print("Time to running in parallel: ", end_time)


# Params definition:
parser = argparse.ArgumentParser(description = "Script for all experiment")

parser.add_argument('-path',
                    help="Path to read files",
                    action='store',
                    dest="path",
                    required=True)

parser.add_argument('-out',
                    help="Path to save the results",
                    action='store',
                    dest='out',
                    required=True)
## For sampling
parser.add_argument('-approach',
                    help="Approach to use",
                    choices=['worlds','programs'],
                    action='store',
                    dest='approach',
                    required=True)

parser.add_argument('-exact',
                    help="(bool) To compute the exact values",
                    action='store_true',
                    dest="exact")

parser.add_argument('-sampling',
                    help='To compute sampling approximation',
                    choices=['info','random'],
                    action='store',
                    dest="sampling")

parser.add_argument('-size',
                    help='Percentage of samples to generate',
                    type=int,
                    action='store',
                    dest='size')

parser.add_argument('-parallel',
                    help="(bool) To run in parallel",
                    action="store_true",
                    dest="parallel")
## For analyze results
parser.add_argument('-analyze',
                    help="(bool) To analyze the results",
                    action='store_true',
                    dest='analyze')

parser.add_argument('-tocsv',
                    help="To generate the results in csv format",
                    choices=['exact','sampling'],
                    action='store',
                    dest="tocsv")
## For test one particular models
parser.add_argument('-test',
                    help="Path of one model",
                    action='store',
                    dest='one_path')

args = parser.parse_args()

exp = Experiment()
# Get all models
if args.one_path:
    models = [args.one_path]
else:    
    models = glob.glob(args.path + 'modeldelp*.json')


# To generate the csv files:
if args.tocsv:
    if args.tocsv == 'exact':
        exp.write_exact_csv(args.path)
    else:
        exp.write_sampling_csv(args.path)
# To analyze the results:
elif args.analyze:
    exp.analyze_results(args.path)
# To run exact:
elif args.exact:
    if args.parallel:
        run_parallel(models, exp, 'exact_sampling', (args.path, args.out, 
                                                                args.approach))
    else:
        exp.exact_sampling(models, args.path, args.out, args.approach)
# To run sampling
elif args.sampling:
    if args.parallel:
        if args.approach == 'worlds':
            # By worlds in parallel
            run_parallel(models, exp, 'by_world_sampling', (args.path, args.out,
                                                            args.size,
                                                            args.sampling))
        else:
            # By delp in parallel
            run_parallel(models, exp, 'by_delp_sampling', (args.path, args.out,
                                                            args.size,
                                                            args.sampling))
    else:
        if args.approach == 'worlds':
            # By worlds in sequential
            exp.by_world_sampling(models, args.path, args.out, args.size, 
                                                                args.sampling)
        else:
            # By delp in sequential
            exp.by_delp_sampling(models, args.path, args.out, args.size, 
                                                                args.sampling)
