import numpy as np

def score(item, bins):
    return -((bins - item) ** 2 + 5.0 * (bins - item) + 25.0)
