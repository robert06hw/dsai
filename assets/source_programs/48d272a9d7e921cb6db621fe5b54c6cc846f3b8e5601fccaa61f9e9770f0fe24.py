import numpy as np

def score(item, bins):
    return -np.power(bins - item - 0.75 * item, 2)
