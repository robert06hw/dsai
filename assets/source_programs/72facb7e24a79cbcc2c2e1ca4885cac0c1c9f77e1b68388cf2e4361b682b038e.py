import numpy as np

def score(item, bins):
    return -np.square(bins - item) / (bins + 1.0) + 0.45 * (bins - item)
