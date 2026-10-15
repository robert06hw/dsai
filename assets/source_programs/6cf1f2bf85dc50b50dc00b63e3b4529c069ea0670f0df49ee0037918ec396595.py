import numpy as np

def score(item, bins):
    return -np.abs((bins - item) - 5.0)
