from bn import *

BNs = ['0','1','2','3','4','5','6','7','8']
alpha = 0.7
path07 = '/home/mario/results/tool/DAQAPExp/30/alpha07/'
path09 = '/home/mario/results/tool/DAQAPExp/30/alpha09/'

for bn in BNs:
     myBN = BayesNetwork(bn + 'TEST', path07)
     myBN.load_bn()
     myBN.make_CPTs(myBN.structure[0], alpha)


def compare_BN(bn):
    myBN = BayesNetwork(bn + 'TEST', path07)
    myBN.load_bn()
    myBN.show_prob_dist(5000)
    myBN = BayesNetwork(bn + 'TEST', path09)
    myBN.load_bn()
    myBN.show_prob_dist(5000)

#compare_BN('2')
