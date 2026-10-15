import numpy as np

def score(item, bins):
    return np.maximum.accumulate(np.maximum(bins - item, 0) - 1.25 * item, axis=0)
