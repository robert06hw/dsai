import numpy as np

def score(item, bins):
    return -(((bins - item) - 20.0) * ((bins - item) - 20.0)) * np.sum((bins - item) > 0)
