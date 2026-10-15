import numpy as np

def score(item, bins):
    return (bins - item) * (bins - item - 25.0) * (bins - item - 25.0) * np.maximum(-100.0, -10.0)
