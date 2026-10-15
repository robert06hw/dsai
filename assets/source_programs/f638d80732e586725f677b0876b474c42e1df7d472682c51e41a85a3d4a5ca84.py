import numpy as np

def score(item, bins):
    return -np.maximum((bins - item) * np.maximum(bins - item - 15.0, 0.0) * ((bins - item) * np.maximum(bins - item - 15.0, 0.0)), 0.0)
