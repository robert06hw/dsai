import numpy as np

def score(item, bins):
    v1 = np.where(bins - item >= 0, bins - item, bins)
    return v1
