import numpy as np

def score(item, bins):
    return np.where((bins >= item) & (bins <= 100 - item), 1, 0)
