from utilsExp import *

# dataDim = 12
# randomNum = np.random.choice(500, 10, replace=True)
# listModelYes = list(map(lambda ints: int_to_bin_with_format(ints, dataDim)[0], randomNum))
# print(listModelYes)

# def checkElements(list):
#     elements = []
#     for i in range(len(list)):
#         if list[i] == 1:
#             elements.append(i)
#     return elements

# programs = [[1,0,1], [1,1,1], [0,1,1],[0,1,1]]
# rules = list(map(checkElements, programs))
# toGraph = list(itertools.chain.from_iterable(rules))
# print(toGraph)


worlds = [[1,0],[0,1]]
completed = completeWorlds(3)
allWorlds = worlds + completed

completedW = [i[0] + i[1] for i in itertools.product(worlds, completed)]
print(len(completedW))


