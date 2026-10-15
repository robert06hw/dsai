import numpy as np

def score(item, bins):
    return -np.square(bins - item) / 2 + np.square(bins - 0.75 * item) / 2
