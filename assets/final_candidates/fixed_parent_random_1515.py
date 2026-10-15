import numpy as np

def score(item, bins):
    return bins * ((bins - item) ** 2 * (bins - item - 25.0))
