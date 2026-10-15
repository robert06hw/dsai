import numpy as np

def score(item, bins):
    return np.minimum(np.minimum(bins - item, np.where(bins - item > 0, bins - item - 25.0, 0)), 0) + np.square(item)
