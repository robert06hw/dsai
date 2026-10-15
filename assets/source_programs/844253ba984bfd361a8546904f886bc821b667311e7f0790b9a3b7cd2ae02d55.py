import numpy as np

def score(item, bins):
    return (-(((bins - item) * (bins - item)) / (bins + 1.0))) + (0.2 * (bins - item))
