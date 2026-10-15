import numpy as np

def score(item, bins):
    return (bins - item - 12.0) * (bins - item - 12.0)
