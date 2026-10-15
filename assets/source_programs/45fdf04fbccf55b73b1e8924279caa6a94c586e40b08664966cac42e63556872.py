import numpy as np

def score(item, bins):
    return np.maximum(np.zeros_like(bins), -(((bins - item) - 18.0) * ((bins - item) - 18.0))) / (bins + 1.0)
