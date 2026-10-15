def score(item, bins):
    residual = bins - item
    return -np.square(1.25 * item - residual)
