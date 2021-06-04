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

    
    def exact_sampling(self, models: list, models_path: str, output: str):
        for model in models:
            index = int(re.search(r'\d+', os.path.basename(model)).group())
            exact = Exact(model, models_path, 'BNdelp' + str(index), output)
            exact.start_exact_sampling()
    
    
    def dist_sampling(self, models: list, models_path: str, output: str, samples: int):
        for model in models:
            index = int(re.search(r'\d+', os.path.basename(model)).group())
            exact_values = read_json_file(os.path.dirname(model)+'/par/'+ os.path.basename(model)[:-5] + 'output.json')
            world_sampling = WorldSampling(model, models_path, 'BNdelp' + str(index), output, exact_values["status"].keys())
            world_sampling.start_distribution_sampling(samples)


    def random_sampling(self, models: list, models_path: str, output: str, samples: int):
        for model in models:
            index = int(re.search(r'\d+', os.path.basename(model)).group())
            exact_values = read_json_file(os.path.dirname(model)+'/par/'+ os.path.basename(model)[:-5] + 'output.json')
            world_sampling = WorldSampling(model, models_path, 'BNdelp' + str(index), output, exact_values["status"].keys())
            world_sampling.start_random_sampling(samples)
    

    def program_random_sampling(self, models, models_path, output, samples):
        for model in models[:1]:
            index =  int(re.search(r'\d+', os.path.basename(model)).group())
            exact_values = read_json_file(os.path.dirname(model) + '/par/' + os.path.basename(model)[:-5] + 'output.json')
            program_sampling = ProgramSampling(model, models_path, 'BNdelp' + str(index), output, exact_values["status"].keys())
            #program_sampling.start_random_sampling(samples)
            program_sampling.start_prefilter_sampling(samples)


    def analyze_results(self, files_path: str):
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


    def write_exact_csv(self, results_path: str) -> None:
        results = glob.glob(results_path + 'modeldelp*output.json')
        fieldnames = ['Prog','Lit', 'Exact', 'Time']
        rows =[]
        for result in results:
            n_program = int(re.search(r'\d+', os.path.basename(result)).group())
            data = read_json_file(result)
            for lit, status in data["status"].items():
                if "flag" in status:
                    rows.append(
                        {
                            'Prog': n_program,
                            'Lit': lit,
                            'Exact': '[' + format(status["l"],'.4f')  +'-'+ format(status["u"],'.4f')  +']',
                            'Time': format(status["time"],'.2f')
                        }
                    )
        ordered_rows = sorted(rows, key=lambda k: k['Prog'])
        with open(results_path + 'csvExact_Results.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ordered_rows)


    def write_sampling_csv(self, results_path: str) -> None:
        results = glob.glob(results_path + 'modeldelp*output.json')
        fieldnames = ['Prog','Lit', 'Intervalo', 'Metric', 'Time', 'Mass']
        rows = []
        for result in results:
            program_name = os.path.basename(result)
            n_program = int(re.search(r'\d+', program_name).group())
            data_sampling = read_json_file(result)
            exact = read_json_file(os.path.dirname(os.path.dirname(os.path.dirname(result)))
                    + '/par/' + program_name)
            for lit, status_lit_e in exact["status"].items():
                if "flag" in status_lit_e:
                    status_lit_s = data_sampling["status"][lit]
                    metric = compute_metric([status_lit_s["l"], status_lit_s["u"]],[status_lit_e["l"], status_lit_e["u"]])
                    mass =  status_lit_s["pyes"] + status_lit_s["pno"] + status_lit_s["pundecided"] + status_lit_s["punknown"]
                    rows.append(
                            {
                                'Prog': n_program,
                                'Lit': lit,
                                'Intervalo': '[' + format(status_lit_s["l"],'.4f')  +'-'+ format(status_lit_s["u"],'.4f')  +']',
                                'Metric': metric,
                                'Time': format(status_lit_s["time"], '.2f'),
                                'Mass': format(mass, '.4f')
                            }    
                        )       
        ordered_rows = sorted(rows, key=lambda k: k['Prog'])
        with open(results_path + 'csvSampling_Results.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ordered_rows)


def exact_parallel(models: list):
    experiment.exact_sampling(models, arguments.path, arguments.out_path) 


def sampling_parallel(models: list, sampling: str):
    if sampling == 'dist':
        experiment.dist_sampling(models, arguments.path, arguments.out_path, int(arguments.size))
    else:
        experiment.random_sampling(models, arguments.path, arguments.out_path, int(arguments.size))

parser = argparse.ArgumentParser(description = " Script for all experiment")
parser.add_argument('-exact',
                    help="(bool) To compute the exact values",
                    action='store_true',
                    dest="exact")
parser.add_argument('-sampling',
                    help='To compute world sampling approximation',
                    choices=['dist','random'],
                    action='store',
                    dest="sampling")
parser.add_argument('-size',
                    help='Number of sample to generate',
                    action='store',
                    dest='size')
parser.add_argument('-path',
                    help="Path to read models",
                    action='store',
                    dest="path",
                    required=True)
parser.add_argument('-analyze',
                    help="(bool) To analyze time and number of interesting literals",
                    action='store_true',
                    dest='analyze')
parser.add_argument('-out',
                    help="Path to save the results",
                    action='store',
                    dest='out_path',
                    required=True)
parser.add_argument('-parallel',
                    help="(bool) To run in parallel",
                    action="store_true",
                    dest="parallel")
parser.add_argument('-tocsv',
                    help="To generate the results in csv format",
                    action='store',
                    dest="tocsv")

arguments = parser.parse_args()

experiment = Experiment()
models = glob.glob(arguments.path + 'modeldelp*.json')
mid = int(len(models)/2)
total_models = len(models)
part1 = models[:mid]
part2 = models[mid:]

if arguments.tocsv:
    if arguments.tocsv == 'exact':
        experiment.write_exact_csv(arguments.path)
    else:
        experiment.write_sampling_csv(arguments.path)
elif arguments.exact:
    if arguments.parallel:
        init_time = time.time()
        p1 = Process(target=exact_parallel, args=(part1,))
        p2 = Process(target=exact_parallel, args=(part2,))
        print_info("Starting in parallel...")
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        end_time = time.time() - init_time
        print("Time to running in parallel: ", end_time)
    else:
        init_time = time.time()
        print_info("Starting in sequencial...")
        experiment.exact_sampling(models, arguments.path, arguments.out_path)
        end_time = time.time() - init_time
        print("Time to run in sequencial: ", end_time)
elif arguments.sampling:
    if arguments.sampling ==  'dist':
        if arguments.parallel:
            init_time = time.time()
            p1 = Process(target=sampling_parallel, args=(part1,'dist',))
            p2 = Process(target=sampling_parallel, args=(part2,'dist',))
            print_info("Starting in parallel...")
            p1.start()
            p2.start()
            p1.join()
            p2.join()
            end_time = time.time() - init_time
            print("Time to running in parallel: ", end_time)
        else:
            init_time = time.time()
            print_info("Starting in sequencial...")
            experiment.dist_sampling(models, arguments.path, arguments.out_path, int(arguments.size))
            end_time = time.time() - init_time
            print("Time to run in sequencial: ", end_time)
    else:
        if arguments.parallel:
            init_time = time.time()
            p1 = Process(target=sampling_parallel, args=(part1,'random',))
            p2 = Process(target=sampling_parallel, args=(part2,'random',))
            print_info("Starting in parallel...")
            p1.start()
            p2.start()
            p1.join()
            p2.join()
            end_time = time.time() - init_time
            print("Time to running in parallel: ", end_time)
        else:
            init_time = time.time()
            print_info("Starting in sequencial...")
            #experiment.random_sampling(models, arguments.path, arguments.out_path, int(arguments.size))
            experiment.program_random_sampling(models, arguments.path, arguments.out_path, int(arguments.size))
            end_time = time.time() - init_time
            print("Time to run in sequencial: ", end_time)
elif arguments.analyze:
    experiment.analyze_results(arguments.path)
