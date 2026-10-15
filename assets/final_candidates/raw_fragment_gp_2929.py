import numpy as np

def score(item, bins):
    return np.minimum((bins - item) ** 2 - 30 * (bins - item), -bins)
