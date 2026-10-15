import numpy as np

def score(item, bins):
    return -(((bins - item) ** 3) * ((bins - item) ** 2))
