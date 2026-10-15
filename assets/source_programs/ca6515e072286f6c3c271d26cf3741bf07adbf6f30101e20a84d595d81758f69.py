import numpy as np

def score(item, bins):
    return -np.minimum(bins - item, bins - item - 25.0)
