def score(item, bins):
    residual = bins - item
    distances = np.maximum(residual, 0)
    squared_distances = distances ** 2
    negative_scores = -squared_distances
    return negative_scores
