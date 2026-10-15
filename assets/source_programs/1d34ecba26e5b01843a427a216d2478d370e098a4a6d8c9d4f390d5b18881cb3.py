import numpy as np

def score(item, bins):
    return -np.multiply(np.square(np.square(bins - item)) - 25.0, np.square(bins - item))
