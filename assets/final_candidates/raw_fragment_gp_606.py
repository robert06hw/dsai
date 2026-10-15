import numpy as np

def score(item, bins):
    return (bins - item) * (np.where(bins - item < 0, 0, bins - item) - 25.0)
