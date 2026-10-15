import numpy as np

def score(item, bins):
    return np.maximum((bins - item) * (bins - item) * (bins - item), 0)
