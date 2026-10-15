import numpy as np

def score(item, bins):
    return np.maximum(0, (bins - item) * ((bins - item) - 25.0)) * ((bins - item) * ((bins - item) - 25.0))
