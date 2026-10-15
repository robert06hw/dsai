import numpy as np

def score(item, bins):
    return -np.multiply(np.subtract(bins, item) - 20.0, np.subtract(bins, item) - 20.0)
