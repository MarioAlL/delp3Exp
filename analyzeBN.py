from bnCode import *
import pyAgrum.lib.bn2graph as gumGraph
import matplotlib.pyplot as plt
from collections import Counter


def showProbDist(path, nSamples):
    bn = loadBN(path)
    gumGraph.dotize(bn, 'BayesianNetwork','pdf')
    samples = [''.join(str(x) for x in world) for [world, asDict] in genSamples(bn, nSamples)]
    toHist=[int(elem,2) for elem in samples]
    
    plt.hist(samples, 10)
    plt.show()
    

showProbDist('./exp1/bn.bifxml', 10000)