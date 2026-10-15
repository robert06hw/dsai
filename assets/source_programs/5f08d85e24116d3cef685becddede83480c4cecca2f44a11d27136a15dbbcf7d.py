import numpy as np

def score(item, bins):
    return -np.sum(np.square(bins - item)) * np.square(bins - item)
