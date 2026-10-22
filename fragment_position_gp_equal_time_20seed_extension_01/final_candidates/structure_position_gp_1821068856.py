def score(item, bins):
    return (np.zeros_like(-bins) - (bins - item)) / np.maximum(np.minimum(bins - item, np.maximum(np.subtract(np.subtract(bins, item), 5.0), 0)), 0.5212328732019077)
