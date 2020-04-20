import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# s = np.random.uniform(-1,0,1000)
# count, bins, ignored = plt.hist(s, 15, density=False)
# #plt.plot(bins, np.ones_like(bins), linewidth=2, color='r')
# print(count[0])
# plt.show()

mu, sigma = 1000, 1 # mean and standard deviation
# s = np.random.normal(mu, sigma, 100)
# count, bins, ignored = plt.hist(s, 10, density=False)
# #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')
# print(count[2])
# print(count[5])
# print(count[9])
# plt.show()

probabilities = []
rnWorlds = []
for i in range(32768):
    rnWorlds.append(np.random.normal(mu,sigma,1))
total = sum(rnWorlds)
print(total)
for i in rnWorlds:
    probabilities.append(float(i)/float(total))
print(sum(probabilities))
plt.hist(probabilities, 10, density=False)
plt.show()