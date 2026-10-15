import numpy as np

def score(item, bins):
    v1 = (bins - item)
    v2 = np.maximum(v1, 0) * np.log(v1 + 1e-10)  # Adjusting for zero values
    v3 = -(v2)
    v4 = (v3 + 25.0)
    v5 = np.maximum(v4, 0)
    return v5
