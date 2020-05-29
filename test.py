from utilsExp import *

# dataDim = 12
# randomNum = np.random.choice(500, 10, replace=True)
# listModelYes = list(map(lambda ints: int_to_bin_with_format(ints, dataDim)[0], randomNum))
# print(listModelYes)
def checkElements(list):
    elements = []
    for i in range(len(list)):
        if list[i] == 1:
            elements.append(i)
    return elements

programs = [[1,0,1], [1,1,1], [0,1,1],[0,1,1]]
rules = list(map(checkElements, programs))
toGraph = list(itertools.chain.from_iterable(rules))
print(toGraph)



