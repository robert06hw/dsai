import numpy as np

def score(item, bins):
    return -((bins - item - 15.0) ** 2 * (bins - item - 15.0 + 1.0)) + np.argmax(bins - item)
