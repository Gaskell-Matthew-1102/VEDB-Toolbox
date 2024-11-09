# Provides operations for two vectors

from math import sqrt

# vec1 - vec2
def vector_subtraction(vec1: tuple, vec2: tuple) -> tuple:
    rel_vec = (
    vec1[0] - vec2[0],
    vec1[1] - vec2[1],
    vec1[2] - vec2[2]
    )
    return rel_vec

def vector_magnitude(vec: tuple):
    magnitude = sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
    return magnitude