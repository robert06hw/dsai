import numpy as np

def score(item, bins):
    return -np.maximum(bins - item, 0) ** 3
