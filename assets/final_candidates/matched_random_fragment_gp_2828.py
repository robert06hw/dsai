import numpy as np

def score(item, bins):
    return np.ones_like(bins) - bins
