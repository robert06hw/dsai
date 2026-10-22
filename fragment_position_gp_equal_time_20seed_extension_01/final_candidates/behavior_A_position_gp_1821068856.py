def score(item, bins):
    return (bins - item) * (bins - item - np.maximum(item - 20.0, 25.0))
