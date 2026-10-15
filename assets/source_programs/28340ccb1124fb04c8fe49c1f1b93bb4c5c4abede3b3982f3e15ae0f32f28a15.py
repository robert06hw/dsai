import numpy as np

def score(item, bins):
    return -(bins - item) * np.square(bins - item - item)
