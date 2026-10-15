import numpy as np

def score(item, bins):
    return -(((bins - item) - 10.0) * ((bins - item) - 10.0))
