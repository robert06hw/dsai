import numpy as np

def score(item, bins):
    return -np.multiply(bins - item, bins - item - 0.75 * item)
