import numpy as np

def score(item, bins):
    # Calculate the distance from each bin to the item
    distances = bins - item
    # Calculate the squared distance
    squared_distances = distances ** 2
    # Calculate the fourth power of the squared distance
    fourth_power_distances = squared_distances ** 2
    # Calculate the score
    score = -((fourth_power_distances - 25.0) * squared_distances)
    return score
