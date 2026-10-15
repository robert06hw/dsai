import numpy as np

def score(item, bins):
    v1 = bins >= item
    v2 = (100.0 - bins) * v1
    return v2
