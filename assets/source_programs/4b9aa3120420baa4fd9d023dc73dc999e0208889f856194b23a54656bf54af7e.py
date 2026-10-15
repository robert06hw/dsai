import numpy as np

def score(item, bins):
    return np.maximum(0, np.minimum(bins - item, 25) * np.minimum(bins - item - 25, bins - item))
