import numpy as np

def score(item, bins):
    return -((bins - item) ** 3 + 25 * bins - 25 * item)
