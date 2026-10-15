import numpy as np

def score(item, bins):
    return np.maximum(0.0, 100.0 - bins)
