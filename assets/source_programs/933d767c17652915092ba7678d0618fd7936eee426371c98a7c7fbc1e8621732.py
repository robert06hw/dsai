import numpy as np

def score(item, bins):
    return np.select(
        condlist=[bins >= item],
        choicelist=[-(bins - item) * (bins - item) / (bins + 1.0) + 0.45 * (bins - item)],
        default=np.inf
    )
