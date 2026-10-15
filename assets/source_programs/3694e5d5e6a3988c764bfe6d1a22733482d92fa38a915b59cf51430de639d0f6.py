import numpy as np

def score(item, bins):
    return -(((bins - item) - 15.0) ** 2) * (bins + 1.0)
