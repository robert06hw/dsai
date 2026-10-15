def score(item, bins):
    residual = bins - item
    max_distance = np.maximum(residual - 5.0, 0.0)
    score = -max_distance * max_distance
    return score
