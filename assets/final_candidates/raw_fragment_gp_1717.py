import numpy as np

def score(item, bins):
    return np.maximum(np.where(bins >= item + 5.0, bins - item - 5.0, np.sum((bins - 0.0) ** 2 / (item + 1.0))), item)
