import pyAgrum as gum
import pyAgrum.lib.bn2graph as gumGraph
from em.bn import *

letters = ['a','b','c','d','e','f','g','h','i','j']
numbers = [0,   1,  2,  3,  4,  5,  6,  7,  8,  9]
# bn = gum.fastBN('0->3<-1;2->3;2->4;3->5;3->6;4->6;6->7;7->5;7->8;7->9',2)
# gum.saveBN(bn, '/home/mario/cyberExampleBN.bifxml')

cyberBN = BayesNetwork('cyberExampleBN', '/home/mario/')
cyberBN.load_bn()
#cyberBN.show_prob_dist(1024)

# bn = gum.loadBN('/home/mario/cyberExampleBN.bifxml')
# generator = gum.BNDatabaseGenerator(bn)
# ie = gum.LazyPropagation(bn)
#
#gumGraph.dotize(bn, '/home/mario/cyberExampleBN', 'pdf')
