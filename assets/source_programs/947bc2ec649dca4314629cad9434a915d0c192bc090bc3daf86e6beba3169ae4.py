import numpy as np

def score(item, bins):
    return -((bins - item) ** 2 - 15.0 * (bins - item) + 225.0) * (bins + 1.0)
