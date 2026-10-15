import numpy as np

def score(item, bins):
    return -bins / np.maximum(np.abs(np.maximum(np.clip(np.tanh(bins), 33.51412398700205 - bins, np.floor(bins)), np.clip(np.round(item), 32.08342117566675, 3.0799690249290967))), 6.519249336540084)
