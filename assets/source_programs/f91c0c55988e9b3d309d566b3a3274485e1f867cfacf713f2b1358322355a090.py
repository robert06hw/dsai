import numpy as np

def score(item, bins):
    return np.where(bins >= item, -((bins - item) * ((bins - item) - 25.0)) * ((bins - item) * ((bins - item) - 25.0)), np.inf)
