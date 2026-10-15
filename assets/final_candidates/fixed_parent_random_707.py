import numpy as np

def score(item, bins):
    return np.minimum(bins - item, 25) * np.minimum(bins - item - 25, bins - item)
