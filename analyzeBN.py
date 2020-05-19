from bnCode import *
import pyAgrum.lib.bn2graph as gumGraph
import matplotlib.pyplot as plt
from collections import Counter
import argparse


def showProbDist(path, nSamples, pathToSave):
    bn = loadBN(path)
    gumGraph.dotize(bn, pathToSave+'BayesianNetwork','pdf')
    samples = [''.join(str(x) for x in world) for [world, asDict] in genSamples(bn, nSamples, pathToSave)]
    toHist=[int(elem,2) for elem in samples]
    plt.hist(toHist, 10)
    plt.show()

    
parser = argparse.ArgumentParser(description="Script to analye the estructure of a BN")

parser.add_argument('-path',
                    help = 'The path to Bayesian Network file (only bifxml)',
                    action = 'store',
                    dest = 'pathToFile',
                    required = True)
parser.add_argument('-s',
                    help='Number of samples to graph the histogram',
                    dest='samples',
                    type=int,
                    required=True)
parser.add_argument('-pathR',
                    help = 'The path to save results',
                    action = 'store',
                    dest = 'pathR',
                    required = True)

arguments = parser.parse_args()

showProbDist(arguments.pathToFile, arguments.samples, arguments.pathR)