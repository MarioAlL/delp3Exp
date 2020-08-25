from bn import *

BNs = ['0','1','2','3','4','5','6','7','8','9']
path07 = '/home/mario/results/tool/DAQAPExp/20/todos/alpha07/'
path09 = '/home/mario/results/tool/DAQAPExp/20/todos/alpha09/'

to_write = ''
for bn in BNs:
     myBN = BayesNetwork(bn + 'TEST', path09)
     myBN.load_bn()
     entropy = myBN.getEntropy()
     to_write += '{:1.2f}'.format(entropy) + '\n'

with open('/home/mario/results/tool/DAQAPExp/10/todos/alpha09/entropy2.txt', 'w') as outfile:
    outfile.write(to_write)
