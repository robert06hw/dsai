import numpy as np

def score(item, bins):
    return -((bins - item) ** 2 - 30 * (bins - item) + 15 * 15) * (bins + 1)
