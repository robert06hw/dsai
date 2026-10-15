import numpy as np

def score(item, bins):
    return -(((bins - item) - 0.75 * item) ** 2)
