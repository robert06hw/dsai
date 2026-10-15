import numpy as np

def score(item, bins):
    return np.maximum.accumulate(bins - item) - 15.0 + (bins - item) * (bins - item) - 1.0 * np.sqrt(np.maximum.accumulate(bins - item))
