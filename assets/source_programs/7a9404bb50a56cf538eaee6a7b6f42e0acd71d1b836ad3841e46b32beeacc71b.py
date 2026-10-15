import numpy as np

def score(item, bins):
    return -bins * (bins - item) * (bins - item - 25.0) * (bins - item - 50.0)
