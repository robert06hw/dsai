import numpy as np

def score(item, bins):
    return -bins / np.maximum(np.abs(bins - 1.0), item)
