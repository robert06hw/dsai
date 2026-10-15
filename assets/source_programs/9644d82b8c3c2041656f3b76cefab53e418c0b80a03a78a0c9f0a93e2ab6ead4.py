import numpy as np

def score(item, bins):
    return -np.minimum((bins - item) ** 2, 25.0) ** 2
