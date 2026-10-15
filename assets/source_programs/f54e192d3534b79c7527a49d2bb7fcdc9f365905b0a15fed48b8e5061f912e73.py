import numpy as np

def score(item, bins):
    return np.maximum(bins - item, 0) ** 3 * np.maximum((bins - item) ** 2 - 5, 0)
