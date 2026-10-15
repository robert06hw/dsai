def score(item, bins):
    score = bins - item - 20.0 / (item + 1.0)
    return np.maximum(score, 0.0)
