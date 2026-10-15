import numpy as np

def score(item, bins):
    return np.select([bins >= item], [((bins - item) - 18.0) * ((bins - item) - 18.0)] / (bins + 1.0))
