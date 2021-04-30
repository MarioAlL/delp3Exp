import sys
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
                    print("Program: " + result)
                    print_ok("Literal: " + key)
                    print_error("[" + "{:.2f}".format(val["l"]) + "-" + "{:.2f}".format(val["u"]) + "]")
                    interest += 1
        print_ok("Total time: " + str(total_time))
        print_ok("Average: " + str(total_time / len(results)))
        print_ok("Interest: " + str(interest))

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


arguments = parser.parse_args()

experiment = Experiment()

if arguments.exact:
    if arguments.parallel:
        p1 = Process(target=exact_parallel, args=(0,5,1))
        p2 = Process(target=exact_parallel, args=(5,10,2))
        print_info("Starting in parallel...")
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    else:
        print_info("Starting in sequencial...")
        experiment.exact_sampling(arguments.path, arguments.out_path, 0, 10)
        print_ok("Complete")
elif arguments.analyze:
    experiment.analyze_results(arguments.path)
