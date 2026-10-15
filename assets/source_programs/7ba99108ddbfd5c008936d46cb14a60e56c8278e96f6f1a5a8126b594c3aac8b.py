import numpy as np

def score(item, bins):
    return np.where(bins >= item, 100 - bins, 0)
