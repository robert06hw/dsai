def score(item, bins):
    return np.multiply(bins - item - 0.75 * item, bins - item - np.argmax(bins - item - 15.0))
