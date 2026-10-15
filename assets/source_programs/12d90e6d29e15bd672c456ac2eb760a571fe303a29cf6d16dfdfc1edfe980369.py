import numpy as np

def score(item, bins):
    return np.full_like(bins, bins - item) - 0.75 * bins
