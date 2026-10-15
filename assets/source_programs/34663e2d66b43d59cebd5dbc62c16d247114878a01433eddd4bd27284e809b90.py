import numpy as np

def score(item, bins):
    return np.select([bins >= item], [np.square(bins - item)], default=np.inf)
