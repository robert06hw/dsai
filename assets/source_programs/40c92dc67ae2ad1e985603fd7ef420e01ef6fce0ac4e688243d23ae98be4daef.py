import numpy as np

def score(item, bins):
    return -((bins - item) * np.clip(bins - item, 0, 10))
