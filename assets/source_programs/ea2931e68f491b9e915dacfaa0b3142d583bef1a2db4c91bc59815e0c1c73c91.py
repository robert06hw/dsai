import numpy as np

def score(item, bins):
    return -np.square(np.maximum(bins - item - 28.0, 0.0))
