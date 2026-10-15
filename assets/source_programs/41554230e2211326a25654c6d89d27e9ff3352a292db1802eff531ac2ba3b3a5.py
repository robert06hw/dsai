import numpy as np

def score(item, bins):
    return -np.clip((bins - item) - 12, 0, 24) ** 2
