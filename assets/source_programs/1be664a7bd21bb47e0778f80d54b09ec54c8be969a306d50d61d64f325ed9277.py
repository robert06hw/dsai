import numpy as np

def score(item, bins):
    return -np.square(bins - item - 28)
