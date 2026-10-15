import numpy as np

def score(item, bins):
    return np.maximum(bins - item + bins, -bins - -100.0)
