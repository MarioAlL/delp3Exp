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
            prnode = "{:.2f}".format(random.uniform(alpha, 1))
            complementnode = "{:.2f}".format(1.00 - float(prnode))
            newCPT = [float(complementnode), float(prnode)]
            if len(parents) != 0:
                parValues = list(itertools.product([1, 0], repeat=len(parents)))
                for parVal in parValues:
                    self.bn.cpt(node)[{str(parents[index]):value for index, value in enumerate(parVal)}] = newCPT
            else:
                self.bn.cpt(node).fillWith(newCPT)
        othersnodes = list(self.bn.nodes())
        for othernode in othersnodes:
            if not othernode in nodes:
                self.bn.generateCPT(othernode)

    def getEntropy(self):
        cNodes = len(self.structure[0])
        samples = list(itertools.product([1,0], repeat=cNodes))
        sum = 0.00
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
    cantNodes = [5, 10, 20]
    alphas = [0.6, 0.8, 0.9]
    results = {
        'entropy_5': [],
        'entropy_10': [],
        'entropy_20': [],
    }

    for cant in cantNodes:
        for i in range(10):
            bn = BayesNetwork('BN' + str(i), '/home/mario/entropy/')
            bn.build_save_random_BN(cant, cant, False)
            nodesInformation = bn.get_nodes_information()
            entropies = []
            for alpha in alphas:
                bn.make_CPTs(nodesInformation['nodes_with_childrens'], alpha)
                entropy = bn.getEntropy()
                entropies.append(entropy)
            results['entropy_' + str(cant)].append(entropies)
        print("\n")
        with open('/home/mario/entropy/entropyResults' + str(cant) + '.json', 'w') as outfile:
            json.dump(results, outfile, indent = 4)



#entropy_test()