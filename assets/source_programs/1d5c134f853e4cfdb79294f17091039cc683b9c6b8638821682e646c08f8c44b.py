import numpy as np

def score(item, bins):
    return -np.where(bins >= item, (bins - item) ** 2, 0)
