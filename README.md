# <h1 align="center">Generate DeLP3E models and sampling</h1>


This repository contains all the files needed to generate DeLP3E models and run the `world sampling` and `subprogram sampling` algorithms.
# Test

`build_datasets`: Script to generate annotations randomly for a DeLP3E program.

optional arguments:
- `-am` AM The path of the dataset with DeLP programs (json).
- `-af` AF_SET Annotation Function setting (`simple`, `medium` or `complex`).
- `-em` EM_SET Environmental Model setting (`simple`, `medium` or `complex`).
- `-out` OUTPUT_PATH Path for the output file
# Tech

This generator is fully developed using `python` and the `Numpy`, `pyAgrum` and `networkx` libraries.

# Licence

GPL-3.0 license