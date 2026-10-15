import numpy as np

def score(item, bins):
    return -np.maximum(bins - item - 5.0, 0) * np.maximum(bins - item - 5.0, 0)
