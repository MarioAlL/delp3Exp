import sys
import csv
import re
from utilsExp import *
from exactSampling import *
import argparse
from multiprocessing import Process

class Experiment:
    def __init__(self):
        pass

    
    def exact_sampling(self, models_path: str, output: str, start: int,
                                                            end: int):
        models = glob.glob(models_path + 'modeldelp*.json')
        for index, model in enumerate(models[start:end]):
            exact = Sampling(model, models_path, 'BNdelp' + str(index), output)
            exact.start_exact_sampling()
    

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


    def write_csv(self, results_path: str) -> None:
        results = glob.glob(results_path + 'modeldelp*output.json')
        fieldnames = ['Prog|Lit', 'Exact', 'Time']
        rows =[]
        for result in results:
            n_program = int(re.search(r'\d+', os.path.basename(result)).group())
            data = read_json_file(result)
            for lit, status in data["status"].items():
                if "flag" in status:
                    rows.append(
                        {
                            'Prog|Lit': str(n_program) + '|' + lit,
                            'Exact': '[' + format(status["l"],'.4f')  +'-'+ format(status["u"],'.4f')  +']',
                            'Time': format(status["time"],'.2f')
                        }
                    )
        with open(results_path + 'csvResults.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def exact_parallel(start: int, end: int, group_id: int):
    experiment.exact_sampling(arguments.path, arguments.out_path, start, end) 
    print_ok("Group " + str(group_id) + " complete")

parser = argparse.ArgumentParser(description = " Script for all experiment")
parser.add_argument('-exact',
                    help="To compute the exact values",
                    action='store_true',
                    dest="exact")
parser.add_argument('-path',
                    help="Path to read files",
                    action='store',
                    dest="path")
parser.add_argument('-analyze',
                    action='store_true',
                    dest='analyze')
parser.add_argument('-out',
                    action='store',
                    dest='out_path')
parser.add_argument('-parallel',
                    help="To run in parallel",
                    action="store_true",
                    dest="parallel")
parser.add_argument('-tocsv',
                    action='store_true',
                    dest="tocsv")


arguments = parser.parse_args()

experiment = Experiment()
if arguments.tocsv:
    experiment.write_csv(arguments.path)
if arguments.exact:
    if arguments.parallel:
        init_time = time.time()
        p1 = Process(target=exact_parallel, args=(0,50,1))
        p2 = Process(target=exact_parallel, args=(50,100,2))
        print_info("Starting in parallel...")
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        end_time = time.time() - init_time
        print("parallel time: ", end_time)
    else:
        init_time = time.time()
        print_info("Starting in sequencial...")
        experiment.exact_sampling(arguments.path, arguments.out_path, 0, 10)
        print_ok("Complete")
        end_time = time.time() - init_time
        print("sequencial time: ", end_time)
elif arguments.analyze:
    experiment.analyze_results(arguments.path)
