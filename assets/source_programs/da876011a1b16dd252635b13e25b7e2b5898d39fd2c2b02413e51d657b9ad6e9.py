import numpy as np

def score(item, bins):
    return -np.power(bins - item - 1.25 * item, 2)
