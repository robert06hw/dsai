import numpy as np

def score(item, bins):
    return -np.minimum(np.minimum(np.minimum(bins - item, bins - item - 25.0), 0), 0)
