import numpy as np

def score(item, bins):
    return -np.square((bins - item) - 0.75 * item)
