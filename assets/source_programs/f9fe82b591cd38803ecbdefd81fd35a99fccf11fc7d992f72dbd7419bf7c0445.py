import numpy as np

def score(item, bins):
    return -np.square(bins - item) + 1.5 * np.square(item)
