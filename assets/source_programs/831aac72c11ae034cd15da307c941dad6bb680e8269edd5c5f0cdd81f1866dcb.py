import numpy as np

def score(item, bins):
    return -np.clip(bins - item, 0.25 * item, 100 - 0.25 * item) ** 2
