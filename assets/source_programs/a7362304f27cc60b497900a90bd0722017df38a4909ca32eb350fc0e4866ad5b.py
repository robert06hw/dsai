import numpy as np

def score(item, bins):
    return np.where((100.0 - bins) * (bins >= item) == np.max((100.0 - bins) * (bins >= item)), 1, 0)
