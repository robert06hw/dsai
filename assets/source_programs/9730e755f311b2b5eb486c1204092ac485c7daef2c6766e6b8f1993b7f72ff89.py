import numpy as np

def score(item, bins):
    return np.where(bins - item >= 0, (bins - item) ** 3, -1.0)
