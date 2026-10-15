import numpy as np

def score(item, bins):
    return (-((bins - item) * (bins - item)) / (item + 1.0)) + (0.3 * (bins - item))
