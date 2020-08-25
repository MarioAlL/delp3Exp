# Class for Bayesian Network
import json

import networkx as nx
import random
import pyAgrum as gum
import pyAgrum.lib.bn2graph as gumGraph
from csv import DictReader
from progress.spinner import Spinner
import matplotlib.pyplot as plt
import itertools
import math
import numpy as np


class BayesNetwork:

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.generator = ''
        self.ie = ''
        self.bn = ''
        self.structure = ''

    def build_save_random_BN(self, nNodes, nEdges, randomCPTs):
        dGraph = create_random_dag(nNodes, nEdges)
        dGraphNodes = dGraph.nodes()
        dGraphEdges = dGraph.edges()
        dGraphEdges = [(str(A), str(B)) for (A, B) in dGraphEdges]
        bn = gum.BayesNet(self.name)
        [bn.add(gum.LabelizedVariable(str(var),str(var),2)) for var in dGraphNodes]
        for edge in dGraphEdges:
            bn.addArc(edge[0], edge[1])
        if randomCPTs:
            bn.generateCPTs() # For generate all CPTs
        gumGraph.dotize(bn, self.path + self.name, 'pdf') # To graph and save BN
        gum.saveBN(bn, self.path + self.name + '.bifxml')
        print("saved")
        self.generator = gum.BNDatabaseGenerator(bn)
        self.ie = gum.LazyPropagation(bn)
        self.bn = bn
        self.structure = [dGraphNodes, dGraphEdges]

    def build_save_BN(self, dGraphNodes, dGraphEdges, randomCPTs):
        dGraphEdges = [(str(A), str(B)) for (A, B) in dGraphEdges]
        bn = gum.BayesNet(self.name)
        [bn.add(gum.LabelizedVariable(str(var),str(var),2)) for var in dGraphNodes]
        for edge in dGraphEdges:
            bn.addArc(edge[0], edge[1])
        if randomCPTs:
            bn.generateCPTs() # For generate all CPTs
        gumGraph.dotize(bn, self.path + self.name, 'pdf') # To graph and save BN
        gum.saveBN(bn, self.path + self.name + '.bifxml')
        self.generator = gum.BNDatabaseGenerator(bn)
        self.ie = gum.LazyPropagation(bn)
        self.bn = bn
        self.structure = [dGraphNodes, dGraphEdges]

    def get_nodes_information(self):
        nodes = list(self.bn.nodes())
        nodes_without_parents = [] # Nodes without parents
        nodes_with_2_parents = [] # Nodes with two parents
        nodes_with_more_parents = [] # Nodes with parents > 2
        nodes_with_childrens = [] # Nodes with at least one children
        for node in nodes:
            parents = len(self.bn.parents(node))
            childrens = len(self.bn.children(node))
            if parents == 0:
                nodes_without_parents.append(node)
            elif parents == 2:
                nodes_with_2_parents.append(node)
            elif parents > 2:
                nodes_with_more_parents.append(node)

            if childrens != 0:
                nodes_with_childrens.append(node)

        nodesInformation = {
            'nodes_no_parents': nodes_without_parents,
            'nodes_2_parents': nodes_with_2_parents,
            'nodes_more_parents': nodes_with_more_parents,
            'nodes_with_childrens': nodes_with_childrens
        }

        return nodesInformation

    def make_CPTs(self, nodes, alpha):
        for node in nodes:
            parents = list(self.bn.parents(node))
            if len(parents) != 0:
                parValues = list(itertools.product([1, 0], repeat=len(parents)))
                for parVal in parValues:
                    prnode = "{:.2f}".format(random.uniform(alpha, 1))
                    complementnode = "{:.2f}".format(1.00 - float(prnode))
                    change_prob = np.random.random()
                    if change_prob > 0.50:
                        newCPT = [float(complementnode), float(prnode)]
                    else:
                        newCPT = [float(prnode), float(complementnode)]
                    self.bn.cpt(node)[{str(parents[index]):value for index, value in enumerate(parVal)}] = newCPT
            else:
                prnode = "{:.2f}".format(random.uniform(alpha, 1))
                complementnode = "{:.2f}".format(1.00 - float(prnode))
                change_prob = np.random.random()
                if change_prob > 0.50:
                    newCPT = [float(complementnode), float(prnode)]
                else:
                    newCPT = [float(prnode), float(complementnode)]
                self.bn.cpt(node).fillWith(newCPT)
        othersnodes = list(self.bn.nodes())
        for othernode in othersnodes:
            if not othernode in nodes:
                self.bn.generateCPT(othernode)
        gum.saveBN(self.bn, self.path + self.name + '.bifxml')
        print("CPTS adapted")

    def getEntropy(self):
        cNodes = len(self.structure[0])
        samples = list(itertools.product([1,0], repeat=cNodes))
        sum = 0.00
        print(len(samples))
        spinner = Spinner("Calculating entropy...")
        for sample in samples:
            evidence = {i: sample[i] for i in range(0, len(sample))}
            prSample = self.get_sampling_prob(evidence)
            if prSample != 0:
                term = prSample * math.log2(prSample)
            else:
                term = 0
            sum += term
            spinner.next()
        spinner.finish()
        return - sum

    def get_probs_Worlds(self, worlds):
        prob = 0.00
        for world in worlds:
            evidence = {i: 1 if world[i] > 0 else 0 for i in range(0, len(world))}
            prob += self.get_sampling_prob(evidence)
        return prob

    def get_sampling_prob(self, evidence):
        self.ie.setEvidence(evidence)
        return self.ie.evidenceProbability()

    def gen_samples(self, samples):
        self.generator.drawSamples(samples)
        self.generator.toCSV(self.path + 'samples.csv')
        samplesToReturn = []
        # Load the csv and return samples as list
        with open(self.path + 'samples.csv', 'r') as read_obj:
            csv_dict_reader = DictReader(read_obj)
            for row in csv_dict_reader:
                asdict = dict(row)
                world = [int(value) for value in list(asdict.values())]
                samplesToReturn.append([world, asdict])
        return samplesToReturn

    def gen_samples_with_prob(self, samples):
        self.generator.drawSamples(samples)
        self.generator.toCSV(self.path + 'samples.csv')
        samplesToReturn = []
        # Load the csv and return samples as list
        with open(self.path + 'samples.csv', 'r') as read_obj:
            csv_dict_reader = DictReader(read_obj)
            spinner = Spinner("Loading samples...")
            for row in csv_dict_reader:
                asdict = dict(row)
                world = [int(value) for value in list(asdict.values())]
                prob = self.get_sampling_prob(asdict)
                samplesToReturn.append([world, asdict, prob])
                spinner.next()
            spinner.finish()
        return samplesToReturn

    def show_prob_dist(self, nSamples):
        samples = [''.join(str(x) for x in world) for [world, asDict] in self.gen_samples(nSamples)]
        toHist=[int(elem,2) for elem in samples]
        plt.hist(toHist, 10)
        plt.show()

    def load_bn(self):
        bn = gum.loadBN(self.path + self.name + '.bifxml')
        self.generator = gum.BNDatabaseGenerator(bn)
        self.ie = gum.LazyPropagation(bn)
        self.bn = bn
        self.structure = [self.bn.nodes(), self.bn.arcs()]

def create_random_dag(nodes, edges):
    # Generate a random DGraph
    G = nx.DiGraph()
    for i in range(nodes):
        G.add_node(i)
    while edges > 0:
        a = random.randint(0, nodes - 1)
        b = a
        while b == a:
            b = random.randint(0, nodes - 1)
        G.add_edge(a, b)
        if nx.is_directed_acyclic_graph(G):
            edges -= 1
        else:
            # Closed a loop
            G.remove_edge(a, b)
    return G

def entropy_test():
    cantNodes = [5, 10, 15]
    alphas = [0.9, 0.95, 0.99]
    nodesToSelect = ['nodes_no_parents','nodes_2_parents', 'nodes_more_parents', 'nodes_with_childrens']

    for alpha in alphas:
        for nodes in cantNodes:
            entropy_in_network = []
            for netNumber in range(9):
                bn = BayesNetwork('BN-' + str(nodes) + '-[' + str(netNumber) + ']', '/home/mario/entropy/')
                bn.build_save_random_BN(nodes, nodes, False)
                bnNodes = bn.get_nodes_information()
                entropy = []
                for selectedNodes in nodesToSelect:
                    bn.make_CPTs([], alpha) # CPTs Random
                    entropyBefore = bn.getEntropy()
                    bn.make_CPTs(bn.structure[0], alpha)
                    entropyAfter = bn.getEntropy()
                    entropy.append([entropyBefore, entropyAfter])
                entropy_in_network.append(entropy)
            e1b, e2b, e3b, e4b = 0, 0, 0, 0
            e1a, e2a, e3a, e4a = 0, 0, 0, 0
            for elem in entropy_in_network:
                e1b += elem[0][0]
                e1a += elem[0][1]
                e2b += elem[1][0]
                e2a += elem[1][1]
                e3b += elem[2][0]
                e3a += elem[2][1]
                e4b += elem[3][0]
                e4a += elem[3][1]

            e1b = e1b / 10
            e1a = e1a / 10
            e2b = e2b / 10
            e2a = e2a / 10
            e3b = e3b / 10
            e3a = e3a / 10
            e4b = e4b / 10
            e4a = e4a / 10

            with open('/home/mario/entropy/entropy-' + str(alpha) + '-' + str(nodes) + '.json', 'w') as outFile:
                entropyResults = {
                    'nodes_no_parents': [e1b, e1a],
                    'nodes_2_parents': [e2b, e2a],
                    'nodes_more_parents': [e3b, e3a],
                    'nodes_with_childrens': [e4b, e4a]
                }
                json.dump(entropyResults, outFile, indent = 4)
