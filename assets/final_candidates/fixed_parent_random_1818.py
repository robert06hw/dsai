import numpy as np

def score(item, bins):
    return np.abs(np.where(bins - item < 0, 0, bins - item - 12.0))
