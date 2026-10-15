import numpy as np

def score(item, bins):
    return np.where(bins - item >= 0, -(((bins - item) * (bins - item)) / (bins + 1.0)) + (0.45 * (bins - item)), np.inf)
