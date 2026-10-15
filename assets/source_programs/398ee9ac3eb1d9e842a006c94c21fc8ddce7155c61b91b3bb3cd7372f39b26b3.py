import numpy as np

def score(item, bins):
    return np.maximum(0, np.maximum(25 - (bins - item), (bins - item) - 25)) * bins
