def score(item, bins):
    return (bins - item) * (bins - item - item) * ((bins - item) * (bins - item - item)) * -10.536012660281536
