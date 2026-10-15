import numpy as np

def score(item, bins):
    return -np.sum(((bins - item)**2) / (item + 1.0)) + 0.3 * (bins - item)
