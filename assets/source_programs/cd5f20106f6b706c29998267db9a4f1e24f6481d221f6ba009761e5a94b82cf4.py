import numpy as np

def score(item, bins):
    return (100.0 - bins) * (bins >= item)
