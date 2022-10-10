import pygame
import numpy as np
from math import sin, cos, atan2, pi, radians, sqrt


def draw_line_dashed(
    surface, color, start_pos, end_pos, width=1, dash_length=10, exclude_corners=True
):

    # convert tuples to numpy arrays
    start_pos = np.array(start_pos)
    end_pos = np.array(end_pos)

    # get euclidian distance between start_pos and end_pos
    length = np.linalg.norm(end_pos - start_pos)

    # get amount of pieces that line will be split up in (half of it are amount of dashes)
    dash_amount = int(length / dash_length)

    # x-y-value-pairs of where dashes start (and on next, will end)
    dash_knots = np.array(
        [np.linspace(start_pos[i], end_pos[i], dash_amount) for i in range(2)]
    ).transpose()

    return [
        pygame.draw.line(
            surface, color, tuple(dash_knots[n]), tuple(dash_knots[n + 1]), width
        )
        for n in range(int(exclude_corners), dash_amount - int(exclude_corners), 2)
    ]

def calculate_bearing(start, end):
    y = sin(radians(end[1] - start[1])) * cos(radians(end[0]))
    x = cos(radians(start[0])) * sin(radians(end[0])) - sin(radians(start[0])) * cos(radians(end[0])) * cos(radians(end[1] - start[1]))
    theta = atan2(y, x)
    return (theta * 180 / pi + 360) % 360

def calculate_distance(start, end):
    # Haversine formula
    lat1 = radians(start[0])
    lon1 = radians(start[1])
    lat2 = radians(end[0])
    lon2 = radians(end[1])

    r = 6371

    dlon = lon2 - lon1
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a)) 
    return r * c
