import numpy as np

def score(item, bins):
    return -(((bins - item) - 40.0) * ((bins - item) - 40.0))
