import numpy as np

def score(item, bins):
    return np.clip(-(((bins - item) - 28.0) * ((bins - item) - 28.0)), 0, np.inf)
