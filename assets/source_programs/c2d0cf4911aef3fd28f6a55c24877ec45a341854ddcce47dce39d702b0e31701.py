def score(item, bins):
    residual = bins - item
    distances = np.maximum(residual - 5.0, 0)
    return -distances ** 2
