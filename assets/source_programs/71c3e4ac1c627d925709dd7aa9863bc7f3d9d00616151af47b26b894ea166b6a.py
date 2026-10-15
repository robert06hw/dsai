import numpy as np

def score(item, bins):
    return -np.where(bins - item > 25.0, np.where(bins - item > 25.0, bins - item - 25.0, 0), 0) ** 3
