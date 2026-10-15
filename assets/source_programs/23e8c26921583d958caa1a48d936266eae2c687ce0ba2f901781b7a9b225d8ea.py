import numpy as np

def score(item, bins):
    return -((((bins - item) ** 2) ** 2 - 25.0) * (bins - item) ** 2)
