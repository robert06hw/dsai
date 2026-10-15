import numpy as np

def score(item, bins):
    return (bins - item) * (bins + 1) * (bins + 2) / 6
