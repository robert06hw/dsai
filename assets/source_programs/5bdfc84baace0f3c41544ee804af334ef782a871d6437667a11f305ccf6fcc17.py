import numpy as np

def score(item, bins):
    return -np.sqrt((bins - item) * (bins - item) * (bins - item) * (bins - item))
