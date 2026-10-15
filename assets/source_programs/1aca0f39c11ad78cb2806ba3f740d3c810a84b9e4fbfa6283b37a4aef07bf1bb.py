import numpy as np

def score(item, bins):
    x = bins - item - 15.0
    return -np.square(np.square(x) + x + 1.0) + np.argmax(x)
