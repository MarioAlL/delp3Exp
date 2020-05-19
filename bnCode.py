import networkx as nx
from random import randint
import pyAgrum as gum
import os
from csv import DictReader
from progress.spinner import Spinner

generator = ''
ie=''

def random_dag(nodes, edges):
    """Generate a random Directed Acyclic Graph (DAG) with a given number of nodes and edges."""
    G = nx.DiGraph()
    for i in range(nodes):
        G.add_node(i)
    while edges > 0:
        a = randint(0,nodes-1)
        b=a
        while b==a:
            b = randint(0,nodes-1)
        G.add_edge(a,b)
        if nx.is_directed_acyclic_graph(G):
            edges -= 1
        else:
            # we closed a loop!
            G.remove_edge(a,b)
    return G


def buildAndSaveBN(nNodes, nEdges, pathToSave):
    dGraph = random_dag(nNodes,nEdges)
    nodes = dGraph.nodes()
    edges = dGraph.edges()
    edges = [(str(A),str(B)) for (A,B) in edges]
    bn=gum.BayesNet('testBN')
    nodebBayes = [bn.add(gum.LabelizedVariable(str(var),str(var),2)) for var in nodes]
    for edge in edges:
        bn.addArc(edge[0],edge[1])
    bn.generateCPTs()
    gum.saveBN(bn,pathToSave+"bn.bifxml")

def loadBN(path):
    global generator, ie
    bn = gum.loadBN(path)
    generator = gum.BNDatabaseGenerator(bn)
    ie = gum.LazyPropagation(bn)
    return bn

def getSamplingProb(evidence):
    # Setting the inference method
    #bn=gum.loadBN('testBN.bifxml')
    # Set the evidence (the value for each variable)
    #ie.setEvidence({'0':1, '1':1, '2':0, '3':1, '4':1, '5':0, '6':1, '7':1, '8':0, '9':1, '10':1, '11':0, '12':1, '13':1, '14':0, '15':1, '16':1, '17':0, '18':1, '19':1})
    ie.setEvidence(evidence)
    # Print the probability for all evidence
    #print(ie.evidenceProbability())
    return ie.evidenceProbability()

#bn = loadBN('testBN.bifxml')
#getSampling(bn)
def genSamples(bn, samples, pathToSave):
    #generator = gum.BNDatabaseGenerator(bn)
    generator.drawSamples(samples)
    generator.toCSV(pathToSave+'samples.csv')
    samplesToReturn = []
    # Load the csv and return samples as list   
    with open(pathToSave + 'samples.csv', 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            asDict = dict(row)
            world = [int(value) for value in list(asDict.values())]
            samplesToReturn.append([world, asDict])
    return samplesToReturn

def genSamplesWithProb(bn, samples, pathToSave):
    generator.drawSamples(samples)
    generator.toCSV(pathToSave+'samples.csv')
    samplesToReturn = []
    # Load the csv and return samples as list   
    with open(pathToSave + 'samples.csv', 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        spinner = Spinner("Loading samples...")
        for row in csv_dict_reader:
            asDict = dict(row)
            world = [int(value) for value in list(asDict.values())]
            prob = getSamplingProb(asDict)
            samplesToReturn.append([world, asDict, prob])
            spinner.next()
        spinner.finish()
    return samplesToReturn


#buildAndSaveBN(3, 3, './exp1/')
# bn = loadBN('./bn.bifxml')
# samples = genSamples(bn, 50)
# for row in samples:
#     print('World:',row[0])
#     print('Evidence:',row[1])